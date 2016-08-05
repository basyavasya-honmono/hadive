## BLOBS+HOG+SVM

1. As sliding window is very slow - blob detection results were used with HOG+SVM model
2. The blob centroids were first calculated - and then sliding window was constructed around that centroid 
3. The features from the patch was then classified by the model
4. Reprediction was not used. Can be used here.
