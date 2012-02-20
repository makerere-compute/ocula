#!/bin/bash

# List the number of annotated objects in each file

#for i in ../../data/train-positive/20110422_14*.jpg
for i in ../../data/test-positive/*.jpg ../../data/test-negative/*.jpg;
do
xmlfile=${i%.*g}.xml
count=`grep object $xmlfile | wc -l`
echo $i, $count; 
done 

