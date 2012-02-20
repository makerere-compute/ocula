'''
Remove any image and annotation files which are marked as bad images.
'''

import glob
from lxml import etree
import os 


# Directory containing marked up images
source_dir = '../../data/train-positive/'

# Directory to move bad images to
bad_dir = '../../data/badimages/'

try:
    os.mkdir(bad_dir)
except:
    pass

# read the list of xml annotation files
xml_files = glob.glob(source_dir + '*.xml')

for annofile in xml_files:
    # extract the bounding boxes from xml
    tree = etree.parse(annofile)

    # check for 'bad image'
    r = tree.xpath('//status/bad')
    badimage = r[0].text=='1'
    
    # if image is not OK, move it and associated data 
    if badimage:
        imagefile = annofile[:-3] + 'jpg'
        os.rename(imagefile, bad_dir+os.path.basename(imagefile))
        os.rename(annofile, bad_dir+os.path.basename(annofile))

