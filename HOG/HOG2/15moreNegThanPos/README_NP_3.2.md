## Model with Neg to Pos Patch Numbers = 1.5

1. The model was trained on test patches containing more negative patches than positive ones (3:2)
2. Only 3000 pos patches were used to train this model. 60:40 split for training and testing was used.
2. The HOG features had n_bins = 36, n_x_cell_pixels = 6, n_y_cell_pixels = 8, signed=True,regularize=False
3. Adaptive Window+Reprediction was used