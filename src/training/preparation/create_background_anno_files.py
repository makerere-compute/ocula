'''
Given a directory of negative images, create corresponding annotation XML files.
'''

import glob
from lxml import etree
import os 


# Directory containing negative images without annotation
source_dir = '../../data/train-negative/'


# read the list of xml annotation files
image_files = glob.glob(source_dir + '*.jpg')

for imagefile in image_files:

    annofilename = imagefile[:-3] + 'xml'

    if not os.path.exists(annofilename):
        tree = etree.parse('empty_annotation.xml')
        tree.find('filename').text = os.path.basename(imagefile)

        outfile = open(annofilename,'w')
        outfile.write(etree.tostring(tree,pretty_print=True))
        outfile.close()

