'''
Randomly select some positive and negative files for the test set.
'''

import glob
import os
import random

# Directory containing source images
neg_dir = '../../data/train-negative/'
pos_dir = '../../data/train-positive/'

# Directories to move test images
test_pos_dir = '../../data/test-positive/'
test_neg_dir = '../../data/test-negative/'

# Size of test set
npos = 700
nneg = 100

#### positive files ######

# read the list of xml annotation files
image_files = glob.glob(pos_dir + '*.xml')

indices = range(len(image_files))
random.shuffle(indices)

for i in range(npos):
    imfile_src = image_files[indices[i]]
    annofile_src = imfile_src[:-3] + 'jpg'

    imfile_dest = test_pos_dir + os.path.basename(imfile_src)
    annofile_dest = test_pos_dir + os.path.basename(annofile_src)

    os.rename(imfile_src, imfile_dest)
    os.rename(annofile_src, annofile_dest)

#### negative files ######

# read the list of xml annotation files
image_files = glob.glob(neg_dir + '*.xml')

indices = range(len(image_files))
random.shuffle(indices)

for i in range(nneg):
    imfile_src = image_files[indices[i]]
    annofile_src = imfile_src[:-3] + 'jpg'

    imfile_dest = test_neg_dir + os.path.basename(imfile_src)
    annofile_dest = test_neg_dir + os.path.basename(annofile_src)

    os.rename(imfile_src, imfile_dest)
    os.rename(annofile_src, annofile_dest)

