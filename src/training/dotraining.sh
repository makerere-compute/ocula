#!/bin/bash

TRAIN_DIR=/home/jq/dev/ocula/data

rm -f $TRAIN_DIR/malariatrain.vec

opencv_createsamples -info $TRAIN_DIR/info.dat -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt -w 40 -h 40 -num `ls $TRAIN_DIR/train-positive/*.xml | wc -l`

mkdir -p $TRAIN_DIR/cascade
rm -f $TRAIN_DIR/cascade/stage* $TRAIN_DIR/cascade/params.xml $TRAIN_DIR/cascade/cascade.xml

opencv_traincascade -w 40 -h 40 -featureType LBP -maxFalseAlarmRate 0.5 -maxDepth 5 -data $TRAIN_DIR/cascade -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt

