## Model with Neg to Pos Patch Numbers = 2

1. The model was trained on test patches containing more negative patches than positive ones (2:1)
2. All positive patches - 10,000 of them were used to train this model. 60:40 split for training and testing was used.
2. The HOG features had n_bins = 18, n_x_cell_pixels = 3, n_y_cell_pixels = 4, signed=True,regularize=False
3. Adaptive Window+Reprediction was used
4. Changing the sliding window movement is possible. (Moving x pixels across and y pixels vertically) and will give be slower or faster depending on how small or large the movements are. 
5.Fast Non-Maximum Supression is used to cluster the patches . The code was taken from [here] (http://www.pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/) and can be found in draw_rects.py