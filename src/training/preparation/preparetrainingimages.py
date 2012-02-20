'''
Script to prepare training data files for cascade training.
'''

import glob
from lxml import etree
import cv

# Whether to make extra background files by drawing white rectangles over the objects
# in positive images.
generate_extra_background_image = False

# Directory containing marked up images
source_dir = '../../data/train-positive/'

# Directory containing background (negative) images
background_dir = '../../data/train-negative/'

# Directory in which to create the info files
out_dir = '../../data/'

infofile = open(out_dir + 'info.dat','w')
backgroundfile = open(out_dir + 'bg.txt','w')

# read the list of xml annotation files
xml_files = glob.glob(source_dir + '*.xml')

for annofile in xml_files:
    # extract the bounding boxes from xml
    tree = etree.parse(annofile)

    # check for 'bad image'
    r = tree.xpath('//status/bad')
    badimage = r[0].text=='1'
    
    # if image is OK, get all the bounding boxes
    if not badimage:
        # load a copy of the image which will have objects covered up
        if generate_extra_background_image:
            background_image = cv.LoadImage(annofile[:-3] + 'jpg')

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
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)
                width = xmax - xmin
                height = ymax - ymin
                if width>10 and height>10:
                    coords = '%s %d %d %d %d' % (coords, xmin, ymin, width, height)
                    nobjects += 1

                    # remove this area for the generated negative image.
                    if generate_extra_background_image:
                        cv.Rectangle(background_image,(xmin,ymin),(xmax,ymax),[255, 255, 255], -1)

            if nobjects>0:
                infofile.write('%s %d %s\n' % (imgfile,nobjects,coords))

        # save background image
        if generate_extra_background_image:
            generated_background_file = 'generatednegative_' + annofile[len(source_dir):-3] + 'jpg'
            cv.SaveImage(background_dir + generated_background_file, background_image)

infofile.close()

# read the list of background images (negative fields of view)
negative_files = glob.glob(background_dir + '*.jpg')

for neg_file in negative_files:
    backgroundfile.write(neg_file[len(out_dir):] + '\n')

backgroundfile.close()

