# Convolutional Neural Network for Pedestrian Classification

![alt text][logo] 
[logo]: https://github.com/gdobler/hadive/blob/master/nn/richard/test/1839jh.gif

### Script definitions
+ **data.lua** Data augmentation and train set class balancing
+ **train.lua** Network training via Stocastic Gradient Descent (SGD)
+ **batchtrain.lua** Network training with Batch Normalization and SGD
+ **imageParamid.lua** Pedestrian detection with exhaustive search

### Dependencies
1. Torch7
   * npy4th
   * penlight
   * math
   * xlua
   * optim
   * image
   * nn / cunn

2. `metrics.lua` within the `scripts/` directory



