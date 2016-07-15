
--[[
@Richard Nam
Input: One full size image
Ouput: Two lua tables (py dictionaries) one with the coordinates of patch, one with the class probabilities
Note: Fixed input size of three
TODO: Create output matrix and fill elements with pixel scores
TODO: Input i/o so it reads images in real-time
TODO: Scoring function for output matrix after smoothing
TODO: Write normalize function in YUV color space
]]

require 'nn'
require 'cunn'
require 'image'
require 'math'

print('START')
-- Read in an image, here as test
full_image = image.load('/home/rnam/Documents/ped/data/2016-04-30-13-09-33_Broadway__169_Street.jpg')
channels = full_image:size()[1]
height = full_image:size()[2]
width = full_image:size()[3]
print(channels, width, height)

print('IMPORT MODEL')
-- import the model table
model_table = torch.load('/home/rnam/Documents/ped/run/output/20160710_full_aug_balanced_m7.net')
-- pull the best model and convert to a double, pull the mean and std and channels
model = model_table.model_best:double()
model:get(20):add(nn.LogSoftMax()):add(nn.Exp()) -- add the softmax
model_mean = model_table.mean
model_std = model_table.std
model_channels = model_table.channels

function ForwardPass(patch, model_channels)
    input_image = image.scale(torch.Tensor(3,32,24),patch:clone())
    trans_image = torch.zeros(input_image:size())
    for i,v in ipairs(model_channels) do
        if model_channels[1]=='r' then
            trans_image[i] = input_image:clone()[{{i},{},{}}]:add(-model_mean[i]) -- remove the mean
            trans_image[i] = trans_image[{{i},{},{}}]:div(model_std[i]) -- devide by the std
        end
    end
    return trans_image:double()
end

-- define fix boxes
boxes = {}
for j=1, 3 do
    boxes[j]={}
end
boxes[1].width=13-1
boxes[1].height=17-1
boxes[2].width=17-1
boxes[2].height=22-1
boxes[3].width=22-1
boxes[3].height=29-1

print('CREATING and NORMALIZE PATCHES')
-- pull the patches based fixed box sizes, also store the upper left (UL) and 
-- lower right (LR) in a different lua table 
timer = torch.Timer()
coords = {}
patches = {}
scores = {}
cnt = 1
for i=1, #boxes do -- this loop is for each box size
    for j=1, height-boxes[i].height do -- this one goes over y axes
        for k=1, width-boxes[i].width do
            top=j
            bottom=j+boxes[i].height
            left=k
            right=k+boxes[i].width
            patch = full_image[{{},{top,bottom},{left,right}}] -- create the patches here
            patches[cnt] = ForwardPass(patch, model_channels)
            coords[cnt] = {left,top,right,bottom} -- saved as UL(x,y), LR(x,y)
            cnt = cnt + 1
        end
    end
end

print('FORWARD PASS')
-- create a tensor to put the patches in 
input_tensor = torch.zeros(#patches,3,32,24)
-- initate a cuda model
model_cuda = model:cuda()
-- put push through the model in batch mode to save memory
bs = 1000
for n=1, input_tensor:size()[1], bs do
    _max = math.min(n+bs,input_tensor:size()[1])
    _input = input_tensor[{{n,_max},{},{},{}}]
    out = model_cuda:forward(_input:cuda())
    _inner = torch.range(n,_max)
    for _j=1, _inner:size()[1] do
        scores[_inner[_j]] = out[_j]:double()
    end
end

print('SAVE')
output = {
    _coords = coords,
    _patches = patches,
    _scores = scores
}
torch.save('forward_output.t7', output)

print('Number of patches: '..#patches..', seconds: '..timer:time().real)

