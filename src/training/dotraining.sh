#!/bin/bash

TRAIN_DIR=/home/jq/data/malaria

opencv_createsamples -info $TRAIN_DIR/info.dat -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt -w 40 -h 40

opencv_haartraining -data $TRAIN_DIR/haarcascade -vec $TRAIN_DIR/malariatrain.vec -bg $TRAIN_DIR/bg.txt -w 40 -h 40 -nonsym -mem 512

#./convert_cascade --size="40x40" $TRAIN_DIR/haarcascade $TRAIN_DIR/haarcascade_plasmodium.xml
