-- training script
-- https://github.com/htwaijry/npy4th
c = require 'trepl.colorize'
npy4th = require 'npy4th'
lapp = require 'pl.lapp'
require 'math'
require 'xlua'
require 'optim'
require 'image'

timer = torch.Timer()
print(c.yellow 'Starting...')
local args = lapp [[
    --save               (default "model_default")               save model name
    --output_dir         (default "output/")                     directory to save the model output
    --model              (default "models/model_baseline.lua")   location of saving the model, full lua filename
    --batch_size         (default 2)                             minibatch size
    --dropout            (default 0.0) 
    --init_weight        (default 0.1)                           random weight initialization limits
    --lr                 (default .001)                          learning rate
    --epochs             (default 4)                             total epochs
    --gpu                                                        train the gru network
    --weigtDecay         (default 0)                             sgd only
    --momentum           (default 0)                             sgd only
    --evaluate           (default 5)                             number of epochs before evaluating
    --gkernel            (default 3)                             gaussian kernel for normalization
    --yuv                                                        flag for converting to YUV color 
    --train_images       (default '/home/rnam/Documents/ped/data/20160626_snapshot/tensors/X_dev.npy') training images
    --train_labels       (default '/home/rnam/Documents/ped/data/20160626_snapshot/tensors/y_dev.npy') training labels
    --test_images        (default '/home/rnam/Documents/ped/data/20160626_snapshot/tensors/X_val.npy') test images
    --test_labels        (default '/home/rnam/Documents/ped/data/20160626_snapshot/tensors/y_val.npy') test labels
    ]]

print(args)
if args.gpu then
    print(c.red 'Training on the gpu')
    require 'cunn'
    -- import model
    local model = nn.Sequential()
    model:add(dofile(args.model))
    model = model:cuda()
    criterion = nn.ClassNLLCriterion():cuda()
    print(model)
else
    print(c.red 'Not training on the gpu')
    require 'nn'
    -- import model
    local model = nn.Sequential()
    model:add(dofile(args.model))
    criterion = nn.ClassNLLCriterion()
    print(model)
end

-- define optimzation criterion
optimState = {
    learningRate = args.lr,
    weightDecay = args.weightDecay,
    momentum = args.momentum,
    learningRateDecay = 1e-7}
optimMethod = optim.asgd
print(c.blue '===>'..' Configuring model')
if model then
   parameters,gradParameters = model:getParameters()
end

-- load data
print(c.blue '===>'..' Loading data')
dimage = npy4th.loadnpy(args.train_images):double()
dlabel = npy4th.loadnpy(args.train_labels):double() + 1
test_image = npy4th.loadnpy(args.test_images):double()
test_label = npy4th.loadnpy(args.test_labels):double() + 1
if args.gpu then dimage = dimage:cuda() end
if args.gpu then test_image = test_image:cuda() end

-- preprocess the data # -- okay
-- convert to color space
if args.yuv then 
    _channels = {'y','u','v'}
    print(c.blue'===>'..' Preprocessing data: colorspace YUV')
    for i = 1, dimage:size()[1] do
        dimage[i] = image.rgb2yuv(dimage[i])
    end
    for i = 1, test_image:size()[1] do
        test_image[i] = image.rgb2yuv(test_image[i])
    end
else
    print(c.blue'===>'..' Preprocessing data: colorspace RGB')
    _channels = {'r','g','b'}
end
    
-- subtract the mean, divide by the std
_mean={}
_std={}
-- normalize each channel in training data globally
for i,channel in ipairs(_channels) do
    _mean[i] = dimage[{ {},i,{},{} }]:mean()
    _std[i] = dimage[{ {},i,{},{} }]:std()
    dimage[{ {},i,{},{} }]:add(-_mean[i])
    dimage[{ {},i,{},{} }]:div(_std[i])
end
-- normalize each channel in test data globally
for i,channel in ipairs(_channels) do
   test_image[{ {},i,{},{} }]:add(-_mean[i])
   test_image[{ {},i,{},{} }]:div(_std[i])
end
-- normalize training set locally
kernel = image.gaussian1D(args.gkernel)
normalization = nn.SpatialContrastiveNormalization(1, kernel):double()
-- normalize all channels locally, TODO: make the cuda() part cleaner
for c in ipairs(_channels) do
    if args.gpu then
        print('Normalizing train on channel: '.._channels[c])
        for i = 1, dimage:size()[1] do
            dimage[{ i,{c},{},{} }] = normalization:forward(dimage[{ i,{c},{},{} }]:double()):cuda()
            xlua.progress(i, dimage:size()[1])
        end
        print('Normalizing test on channel: '.._channels[c])    
        for i = 1, test_image:size()[1] do
            test_image[{ i,{c},{},{} }] = normalization:forward(test_image[{ i,{c},{},{} }]:double()):cuda()
            xlua.progress(i, test_image:size()[1])
        end
    else
        print('Normalizing train on channel: '.._channels[c])       
        for i = 1, dimage:size()[1] do
            dimage[{ i,{c},{},{} }] = normalization:forward(dimage[{ i,{c},{},{} }])
            xlua.progress(i, dimage:size()[1])
        end
        print('Normalizing test on channel: '.._channels[c])
        for i = 1, test_image:size()[1] do
            test_image[{ i,{c},{},{} }] = normalization:forward(test_image[{ i,{c},{},{} }])
            xlua.progress(i, test_image:size()[1])
        end
    end
end

-- new training methods
print(c.blue '===>'..' Training')
for e=1, args.epochs do
    -- confusion matrix for training
    classes = {'1','2'}
    confusion = optim.ConfusionMatrix(classes)
    rand = torch.randperm(dimage:size()[1]) -- randomize indexes
    for step=1, dimage:size()[1], args.batch_size do
        -- disp progress
        xlua.progress(step, dimage:size()[1])
        local labels = {}
        local images = {}
        for i=step, math.min(step+args.batch_size-1, dimage:size()[1]) do
            label = dlabel[rand[i]]
            image = dimage[rand[i]]
            table.insert(labels, label)
            table.insert(images, image)
        end
        -- mini-batch evaluation
        local feval = function(x)
            -- new parameters
            if x ~= parameters then
                parameters:copy(x)
            end
            -- reset gradients
            gradParameters:zero()
            -- mean of all the criterions
            f = 0
            -- evalute for the entire mini-batch
            for j=1, #images do
                D = images[j]
                glabel = labels[j]
                -- estimate f (for the entire mini-batch)
                local output = model:forward(D)
                local err = criterion:forward(output, glabel)
                f = f + err
                -- compute the derivative and update the model
                local df = criterion:backward(output, glabel)
                model:backward(D, df)
                -- update confusion
                confusion:add(output, glabel)
            end
            -- normalize the gradients
            gradParameters:div(#images)
            f = f/#images
            return f, gradParameters
        end
        _new_x, _fx , _average = optimMethod(feval, parameters, optimState)     

    end
    print(c.yellow 'Completed epoch: '..e)
    print(confusion)
    -- evaluate the model after N number of epochs
    if e % args.evaluate == 0 then
        print(c.red '===>'..' Evaluate at epoch: '..e)
        _confusion = optim.ConfusionMatrix(classes)
        model:evaluate()
        for _t = 1, test_image:size()[1] do
            xlua.progress(_t, test_image:size()[1])
            _input = test_image[_t]
            _target = test_label[_t]
            local _pred = model:forward(_input)
            _confusion:add(_pred, _target)
        end
        print(_confusion)
        print(c.red '===>'..' Saving model to '..args.output_dir..args.save..'.net')
        dump = {
            model=model,
            mean=_mean,
            mean=_std,
            channels=_channels
            }
        torch.save(args.output_dir..args.save..'.net', dump)
    end
end


print('Time elapsed for '..args.epochs..' epochs ' .. timer:time().real/60 .. ' minutes')
print(c.yellow 'made it to the end')







