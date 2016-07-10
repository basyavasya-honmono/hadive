#!/bin/bash
#PBS -l nodes=1:ppn=1:gpus=1
#PBS -l walltime=90:00:00
#PBS -l mem=30GB
#PBS -N second
module purge

module load torch-deps/7
module load torch/intel/20151009

cd /home/bt1085/hadive/nn/bibby/
th train.lua
