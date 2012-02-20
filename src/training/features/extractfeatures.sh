#!/bin/bash

# Apply feature extraction to all image files in specified folders.

for i in ../../data/train-positive/20110422_14*.jpg
#for i in ../../data/train-positive/*.jpg ../../data/train-negative/*.jpg ../../data/test-positive/*.jpg ../../data/test-negative/*.jpg;
#for i in ../../data/train-smallset/*.jpg;
do
outfile=${i%.*g}
#./feature_densesurf $i 25 25 30 1 0 > "$outfile.surf_25_30"
./feature_moments.py $i 25 25 30 > "$outfile.moments_25_30"
#./feature_detectionoutput.py $i 25 25 30 cascade > "$outfile.cascade_25_30"
#./feature_traintargets.py $i 25 25 30 cascade > "$outfile.traintargets_25_30"
#./feature_detectionoutput.py $i 25 25 30 boost-surf > "$outfile.boost-surf_25_30"
#./feature_detectionoutput.py $i 25 25 30 boost-moments > "$outfile.boost-moments_25_30"
echo "$outfile" ; 
done 

