<h1 align="center">
    <a href=https://serv.cusp.nyu.edu/projects/HaDiVe-Temp/>HaDiVe</a>
</center>

## Overview
The Human Detection in Video (HaDiVe) project is a culmination of work undertaken by faculty and students at the NYU Center for Urban Science + Progress. Using [publicly available video streams](http://dotsignals.org/) the HaDiVe project aims to create a real-time pedestrian counter within New York City. At present, counts are recorded at approximately one minute intervals for each camera. Ultimately, this is being accomplished using a Faster Region-based Convolutional Neural Network (Faster R-CNN) trained with a hand-labelled set of DOT images.

With the current training and test set, the Faster R-CNN is achieving 51% precision identifying people. Together, the images below illustrate the current successes and shortcomings of the current iteration. As seen, the model is confidently identifying individuals in the foreground of the images. However, individuals who are distant from the camera or partially occluded are not being identified. Expanding the current training set is likely to improve overall performance. Nonetheless, current results can inform the relative number of pedestrians throughout the city at an granular temporal scale.

<p align="center">
<img src="https://serv.cusp.nyu.edu/projects/HaDiVe-Temp/images/ex1.png" width="350"/> <img src="https://serv.cusp.nyu.edu/projects/HaDiVe-Temp/images/ex2.png" width="350"/> 
</center>

__This repo includes: (1) all training data; (2) tools to create additional training data; (3) the tools to collect pedestrian counts; and, (4) supplementary scripts.__

## Creating Training Data
Training data follows the VOC format. Raw data (in sqlite3 database), original .jpg files, and corresponding .xml files are stored under `hadive/data/training/`. Training and testing sets are listed in .txt files following a 70/30 train-test split.

To create additional training data, navigate to `hadive/hadive/create_training_data/`. Then, download n images to label. 
```
python scrape_training_data.py --count 5     # (e.g., n = 5)
```
To label the downloaded images, run the snippet below. Boxes are created by clicking head to toe, boxes will be drawn using an aspect ratio of 3:4. Pos examples will be colored red and negative examples blue. The following keystrokes may be used: 
1. up-arrow: toggle between 'pos' and 'neg' label.
2. left-arrow: remove previous box.
3. right-arrow: next image.
```
python label_training_data.py
```
Last, to create xml files for newly labeled data and update the train-test split .txt files run:
```
python create_training_data.py
```

## Training & Testing
Training and testing is accomplished by following the [Faster-RCNN_TF documentation](https://github.com/smallcorgi/Faster-RCNN_TF/blob/master/README.md), and replacing the VOC training data with the created training data.

## Counting Pedestrians
Download `VGGnet_fast_rcnn_iter_90000.ckpt*` files (to be hosted somewhere) and store in `hadive/data/external/`. Navigate to `hadive/hadive/lib/` and run `make`. Subsequently, navigate to `hadive/hadive/tools/` and run:
```
python ped-count-sqlite.py --model ../../data/external/VGGnet_fast_rcnn_iter_90000.ckpt --duration n     # Where n is the number of loops through all cameras
```

## Recommendations
It is recommended to use GPUs when counting pedestrians.

## Project Organization
```
├── README.md
├── data
│   ├── training  
│   │   ├── img               <- All training .jpgs
│   │   ├── xml               <- All training .xmls
│   │   ├── txt               <- Train-test split (70/30) .txt lists
│   │   └── training.db       <- Image (table: images) and label (table: labels) data.
│   ├── external              <- Downloaded tensorflow .ckpt files.
│   └── results               <- Camera (table: cameras) and pedestrian counts (table: ped_counts) data.
└── hadive
    ├── create_training_data  <- Scripts to scrape, label, and write additional training data.
    ├── experiments
    ├── lib
    └── tools                 <- Scripts to count pedestrians.

```

## Credit
This project uses [smallcorgi/Faster-RCNN_TF](https://github.com/smallcorgi/Faster-RCNN_TF)
