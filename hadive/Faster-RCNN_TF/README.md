# Hadive Faster-RCNN

### Setup on critter
1. Clone Faster-RCNN_TF and hadive to critter: 
	```
	git clone https://github.com/smallcorgi/Faster-RCNN_TF.git
	git clone https://github.com/gdobler/hadive.git
	```
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
	
### Training on DOT Training Data (on critter, within Faster-RCNN_TF/)
1. Copy DOT training data to `/data/VOCdevkit2007`:
	```
	mkdir data/VOCdevkit2007
	cp -r <Annotations folder> data/VOCdevkit2007/
	cp -r <JPEGImages folder> data/VOCdevkit2007/
	```
2. Replace `experiments/cfgs/faster_rcnn_end2end.yml`:
	```
	rm experiments/cfgs/faster_rcnn_end2end.yml
	cp ../hadive/hadive/Faster-RCNN_TF/faster_rcnn_end2end.yml experiments/cfgs/
	```
3. Create `output.txt` to append std output:
	```
	touch output.txt
	```
4. Train network, while appending std output to output.txt:
	```
	python ./tools/train_net.py --device GPU --device_id 0 --weights data/pretrain_model/VGG_imagenet.npy --imdb voc_2007_trainval --iters 50000 --cfg experiments/cfgs/faster_rcnn_end2end.yml --network VGGnet_train > output.txt &
	```
5. Concurrently, delete extra .ckpt files as new ones are output:
	```
	python ../hadive/hadive/Faster-RCNN_TF/del_ckpt.py --path output/faster_rcnn_end2end/voc_2007_trainval/ --iters <iters for training> &
	```
	
### Notes
1. Should improve data prep process.
2. Should change naming, so we're not using the VOCdevkit naming.
3. Runtime of approx 2:15hrs for 50,000 iters.

### Organization
```
Faster-RCNN_TF
    ├── tools
    ├── output                     <- Directory to store tensorflow .ckpt files
    ├── lib
    ├── experiments
    │   └── cfgs                   <- Configuration .yml for training
    └── data
        ├── cache
        ├── pretrain_model         <- Includes VGG_imagenet.npy
        └── VOCdevkit2007          <- Includes Annotations & JPEGImages
```
