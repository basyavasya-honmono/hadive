# Convolutional Neural Network for Pedestrian Classification

![alt text][logo] 
[logo]: https://github.com/gdobler/hadive/blob/master/nn/richard/test/1839jh.gif

### Script definitions
+ **createPatchs.py** Creates patches for input into CNN
+ **data.lua** Data augmentation and train set class balancing
+ **train.lua** Network training via Stocastic Gradient Descent (SGD)
+ **batchtrain.lua** Network training with Batch Normalization and SGD
+ **imageParamid.lua** Pedestrian detection with exhaustive search

### Dependencies
1. Python 2.7+
   * numpy
   * pandas
   * scikit-learn
   * PIL
   * argparse

2. Torch7
   * npy4th
   * penlight
   * math
   * xlua
   * optim
   * image
   * lfs
   * nn / cunn

3. `metrics.lua` within the `scripts/` directory

### Training the model from start to finish
Training the model requires extracting the label patches and converting them to torch tensors `createPatches.py`. Then training the network with either a mini-batch SGD strategy `train.lua` or a mini-batch SGD strategy with Batch Normalization `batchtrain.lua`. Optionally, if there is an imbalanced between the two classes the `data.lua` script will balance the data via data augmentation. This last script can be run after extracting the patches. 

