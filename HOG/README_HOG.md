## HOG BASED SVM MODEL

1. HOG1 contains basic gradients visualization of patches
2. HOG2 contains hog features scripts and 3 models 
	* No. of POS Patches = 3000,N:P = 1.5, HOG Params as follows: n_bins = 36, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed=True,regularize=False
	* No. of POS Patches = 10,000,N:P = 2, HOG Params as follows: n_bins = 18, n_x_cell_pixels = 3, n_y_cell_pixels = 4, signed=True,regularize=False
	* Blob based

3. Adaptive Windowing was used for sliding window while testing (taking perspective into account)
4. Reprediction to reduce false positives with different thresholds was also used.
5. Sequence 
	* hog folder to understand feature extraction [1](https://github.com/gdobler/hadive/tree/master/HOG/HOG2/hog)
	* Parameter sweeps and instant new model creation [2](https://github.com/gdobler/hadive/tree/master/HOG/HOG2/RunModels)
	* Model with N:P = 1.5 with simple live_adaptive window script demo [3](https://github.com/gdobler/hadive/tree/master/HOG/HOG2/15moreNegThanPos)
	* Model with N:P = 2 with reprediction and better trained model with more training data [4](https://github.com/gdobler/hadive/tree/master/HOG/HOG2/allPatches)
	* Blob based Model [5](https://github.com/gdobler/hadive/tree/master/HOG/HOG2/BLOBS_HOG_SVM)