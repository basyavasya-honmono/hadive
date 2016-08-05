## HOG Feature Extraction in Python

Inspiration :
1. [Dalal and Triggs](https://lear.inrialpes.fr/people/triggs/pubs/Dalal-cvpr05.pdf)
2. [Dalal HOG Video](https://www.youtube.com/watch?v=7S5qXET179I)
3. [Tutorial](http://mccormickml.com/2013/05/09/hog-person-detector-tutorial/)
4. [Python Script](https://github.com/gdobler/hadive/blob/master/HOG/HOG2/hog/hog_signed.py)



### Details

1. The default parameters are n_bins = 18, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed = True, regularize=False
2. Block normalization is always set to 50% and patches are converted to grayscale when input.
3. Non-local denoising of the patches is performed when input
4. The patches are resized before HOG Features are extracted to width = 24 and height = 32.

1. The two scripts are similar - except the one-hog_signed.py returns the path of the labeled patch from the database/file (and hence was used during training of the model) and the other was used during testing using sliding window. As these two processes (training a model and testing an image) were done simultaneously for different models, two different scripts were created, to keep them independent of each other.	
