#!/usr/bin/python
'''
Calculate dense cascade features across an image

Usage: 
feature_cascade.py filename xstep ystep size detectortype

detectortype should be cascade|boost-surf|boost-moments

Output:
One line for each image position of the form:
x y size class
where class is 1 or 0 indicating object presence.
'''

import sys
sys.path.append('../detection')
sys.path.append('../evaluation')

import glob
from lxml import etree
import cv
import os
import copy
import sys
import cascadedetect
import boosteddetect
import findaccuracy

if __name__=='__main__':
    imagefilename = sys.argv[1]
    xstep = int(sys.argv[2])
    ystep = int(sys.argv[3])
    size = int(sys.argv[4])

    boundingboxes = findaccuracy.getboundingboxes(imagefilename)

    # Scan through patch locations in the image
    patchidx = 0
    im = cv.LoadImage(imagefilename)
    width = im.width
    height = im.height
    x = xstep
    y = ystep
    while y<height:
        x = xstep;
        while (x<width):
            objecthere=0
            for bb in boundingboxes:
                # If the detected centre falls in the middle of a whitefly bounding
                # box, then it's a true positive.

                xmin = bb[0]
                xmax = bb[1]
                ymin = bb[2]
                ymax = bb[3]
                bbx = (xmin+xmax)/2
                bby = (ymin+ymax)/2
                #if xkey>xmin and xkey<xmax and ykey>ymin and ykey<ymax:
                # check whether a given proportion of overlap, such that there is exactly one match
                # per patch
                if (bbx<x+xstep-size/2.0 and 
                    bbx>x-size/2.0 and 
                    bby<y+ystep-size/2.0 and 
                    bby>y-size/2.0):

                    objecthere = 1
                    break
    
            # Output the details for this patch
            print "%d %d %d %d" % (x,y,size,objecthere)

            x+=xstep;
        y += ystep;

