'''
Script to prepare training data files for haartraining.
'''

import glob
from lxml import etree

# Directory containing marked up images
source_dir = '/home/jq/data/malaria/200/'

# Directory containing background (negative) images
background_dir = '/home/jq/data/malaria/negative/'

# Directory in which to create the info files
out_dir = '/home/jq/data/malaria/'

infofile = open(out_dir + 'info.dat','w')
backgroundfile = open(out_dir + 'bg.txt','w')

# read the list of xml annotation files
xml_files = glob.glob(source_dir + '*.xml')

for annofile in xml_files:
    # extract the bounding boxes from xml
    tree = etree.parse(annofile)
    
    r = tree.xpath('//bndbox')
    infoline = ''
    nobjects = 0
    imgfile = annofile[len(out_dir):-3] + 'jpg'
    coords = ''
    if (len(r) != 0):
        for i in range(len(r)):
            xmin = round(float(r[i].xpath('xmin')[0].text))
            xmin = max(xmin,1)
            xmax = round(float(r[i].xpath('xmax')[0].text))
            ymin = round(float(r[i].xpath('ymin')[0].text))
            ymin = max(ymin,1)
            ymax = round(float(r[i].xpath('ymax')[0].text))
            width = xmax - xmin
            height = ymax - ymin
            if width>10 and height>10:
                coords = '%s %d %d %d %d' % (coords, xmin, ymin, width, height)
                nobjects += 1
        if nobjects>0:
            infofile.write('%s %d %s\n' % (imgfile,nobjects,coords))

infofile.close()

# read the list of background images (negative fields of view)
negative_files = glob.glob(background_dir + '*.jpg')

for neg_file in negative_files:
    backgroundfile.write(neg_file[len(out_dir):] + '\n')

backgroundfile.close()

