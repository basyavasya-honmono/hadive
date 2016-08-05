## Running Models

The script (parameter_sweep_SVMModel.py) is used to find the optimum parameters for the SVM Model (trained on the manually label patches).
Choosing the right C and gamma with high accuracy, precision and recall, will result in a model that will then be used for sliding window testing on test images
Inspiration: [SVM Sklearn RBF Parameters](http://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html)

## Key Points

1. C and gamma are moving in logspace, so don't let negative values for these two in function surprise/confuse you.
2. You can change the parameters for hog features. The numbers on bins, x_cell_width,y_cell_width, orientation, regularization. Block overlap of 50% is used always.
3. But note that you cannot change these parameters during testing with sliding window on patches as feature length will differ as you will be working on this pre-trained model.
The best performance was given for n_bins = 18, x_cell_width = 3,y_cell_width=4, orientation=signed, regularization=False.

4. The accuracy, precision, recall, which patch got classified as TP,FP,TN,FN can all be seen. If you do not wish to get that information, you can uncomment those lines and proceed. Please note this kind of information might come in handy during negative-hard mining.

5. You can also experiment with the ratio of positive to negative patches. Taking 1:1, 1:1.5,1:2, the best performance with sliding window comes with 1:2 amongst these three that were tried.

