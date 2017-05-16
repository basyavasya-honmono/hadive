#!/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mem=16000
#SBATCH --job-name=train_orig_VOC
#SBATCH --mail-type=END
#SBATCH --mail-user=jmv423@nyu.edu
#SBATCH --output=std_output%j.txt

# Set up the environment
module purge
module load tensorflow/python2.7/20170218
module load opencv/intel/3.2
module load pillow/intel/4.0.0
module load scikit-learn/intel/0.18.1

# Run script

cd /home/jmv423/Faster-RCNN_TF/
touch output.txt

python ./tools/train_net.py --device GPU --device_id 0 --weights data/pretrain_model/VGG_imagenet.npy --imdb voc_2007_trainval --iters 70000 --cfg experiments/cfgs/faster_rcnn_end2end.yml --network VGGnet_train > output.txt
