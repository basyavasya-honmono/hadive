# Hadive Faster-RCNN

### Setup on critter
1. Clone Faster-RCNN_TF to critter: `git clone https://github.com/smallcorgi/Faster-RCNN_TF.git`
2. Replace `Faster-RCNN_TF/lib/` with `hadive/hadive/Faster-RCNN_TF/lib/`: 
	```
	rm -r Faster-RCNN_TF/lib/
	cp -r hadive/hadive/Faster-RCNN_TF/lib/ Faster-RCNN_TF/
	```
3. Build Cython modules:
	```
	cd Faster-RCNN_TF/lib/
	make
	```
4. Download the pre-trained ImageNet models:
   	```
	cd ..
	mkdir data/pretrain_model/
   	wget https://www.dropbox.com/s/po2kzdhdgl4ix55/VGG_imagenet.npy?dl=0# -O data/pretrain_model/VGG_imagenet.npy
	```
	
### Creating DOT Training Data
1. On compute run `VOC_xml_format.py`:
	```
	python ./VOC_xml_format.py --path <Location to save .xml & .jpg files>
	```
2. To clean the dataset, run `VOC_xml_rm.py`:
	```
	python ./VOC_xml_rm.py --path <Location with saved .xml & .jpg files>
	```
	
### Training on DOT Training Data
1. Copy DOT training data to `/data/VOCdevkit2007`:
	```
	mkdir data/VOCdevkit2007
	cp -r <Annotations folder> data/VOCdevkit2007/
	cp -r <JPEGImages folder> data/VOCdevkit2007/
	```
2. Create `output.txt` to append std output:
	```
	touch output.txt
	```
3. Train network, while appending std output to output.txt:
	```
	python ./tools/train_net.py --device GPU --device_id 0 --weights data/pretrain_model/VGG_imagenet.npy --imdb voc_2007_trainval --iters 70000 --cfg experiments/cfgs/faster_rcnn_end2end.yml --network VGGnet_train > output.txt &
	```
### Notes
1. I've been renaming the VOCdevkit2007_orig & VOCdevkit2007_resized to VOCdevkit when training.
2. The cache need to be cleared when switching between the original and resized data.
3. Should delete unnecessary .ckpt files as they're produced.
4. Approximate runtime of 13:00 hrs for 70,000 iters.


### Organization
```
Faster-RCNN_TF
    ├── tools                      <- .py scripts from Faster-RCNN_TF Repo
    ├── output                     <- Directory to store tensorflow .ckpt files #When is this created?
    ├── lib                        <- Faster RCNN code
    ├── experiments
    │   └── cfgs                   <- Configuration .yml for training
    └── data
        ├── cache
        ├── demo
        ├── pretrain_model         <- Includes VGG_imagenet.npy
        ├── VOCdevkit2007_orig     <- Original VOC training data.
        └── VOCdevkit2007_resized  <- Resized VOC training data           
```
