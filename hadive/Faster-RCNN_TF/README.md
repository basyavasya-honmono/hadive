# Hadive Faster-RCNN

### Setup
1. Clone [Faster-RCNN_TF Repo]('https://github.com/smallcorgi/Faster-RCNN_TF') to $USER directory on Prince.
2. Edit CUDA_PATH in /lib/make.sh to '/share/apps/cuda/8.0.44'
3. Edit CUDAHOME in /lib/setup.py to 'CUDA_HOME'
4. Download the training, validation, test data and VOCdevkit
	```Shell
	wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval_06-Nov-2007.tar
	wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtest_06-Nov-2007.tar
	wget http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCdevkit_08-Jun-2007.tar
	```
5. Extract all of these tars into one directory named `VOCdevkit`
	```Shell
	tar xvf VOCtrainval_06-Nov-2007.tar
	tar xvf VOCtest_06-Nov-2007.tar
	tar xvf VOCdevkit_08-Jun-2007.tar
	```
6. Create symlinks for the PASCAL VOC dataset
	```Shell
    cd $FRCN_ROOT/data
    ln -s $VOCdevkit VOCdevkit2007
    ```
7. Download the pre-trained ImageNet models [[Google Drive]](https://drive.google.com/open?id=0ByuDEGFYmWsbNVF5eExySUtMZmM) [[Dropbox]](https://www.dropbox.com/s/po2kzdhdgl4ix55/VGG_imagenet.npy?dl=0)
   	```Shell
    mv VGG_imagenet.npy $FRCN_ROOT/data/pretrain_model/VGG_imagenet.npy
    ```

### Training Original Dataset
1. Submit job using [train_VOC.sh](https://github.com/gdobler/hadive/blob/master/hadive/train_VOC.sh)
```SBATCH train_VOC.sh```

### Training Resized Dataset
1. Create an output directory for resized .jpeg and .xml files.
2. Edit [VOC_resize](https://github.com/gdobler/hadive/blob/master/hadive/VOC_resize.sh), to include proper paths:
```
if __name__ == '__main__':
	main('$USER/VOCdevkit/VOC2007/', '$USER/VOCdevkit/Resampling', 32.4)
```
3. Copy VOCdevkit2007 (i.e., VOCdevkit2007_resized) and replace JPEGImages & Annotations with resampled files.
4. Edit lib/datasets/pascal_voc.py function `_load_pascal_annotation(self, index)`:
```
 for ix, obj in enumerate(objs):
            bbox = obj.find('bndbox')
            # Make pixel indexes 0-based
            x1 = float(bbox.find('xmin').text)
            y1 = float(bbox.find('ymin').text)
            x2 = float(bbox.find('xmax').text)
            y2 = float(bbox.find('ymax').text)
```
5. Edit `experiments/cfgs/faster_rcnn_end2end.yml` to include `USE_FLIPPED: False` under `TRAIN:` # This should be fixed.
6. Submit job using [train_VOC.sh]('https://github.com/gdobler/hadive/blob/master/hadive/train_VOC.sh')
```SBATCH train_VOC.sh```

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