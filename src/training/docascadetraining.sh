#!/bin/bash

TRAIN_DIR=../../data

#rm -f $TRAIN_DIR/malariatrain.vec
#opencv_createsamples -info $TRAIN_DIR/info.dat -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt -w 12 -h 12 -num 35000

mkdir -p $TRAIN_DIR/cascade
rm -f $TRAIN_DIR/cascade/stage* $TRAIN_DIR/cascade/params.xml $TRAIN_DIR/cascade/cascade.xml

opencv_traincascade -w 12 -h 12 -featureType LBP -mode ALL -minHitRate 0.995 -maxFalseAlarmRate 0.4 -maxDepth 5 -numPos 6000 -numNeg 3000 -numStages 10 -precalcValBufSize 512 -precalcIdxBufSize 512 -data $TRAIN_DIR/cascade -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt

