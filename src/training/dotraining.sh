#!/bin/bash

TRAIN_DIR=/home/jq/dev/ocula/data

#opencv_createsamples -info $TRAIN_DIR/info.dat -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt -w 40 -h 40 -num `ls $TRAIN_DIR/train-positive/*.xml | wc -l`

opencv_traincascade -featureType LBP -data $TRAIN_DIR/cascade -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt -w 40 -h 40

#./convert_cascade --size="40x40" $TRAIN_DIR/haarcascade $TRAIN_DIR/haarcascade_plasmodium.xml
