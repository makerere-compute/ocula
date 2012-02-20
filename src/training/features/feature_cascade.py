#!/usr/bin/python
'''
Calculate dense cascade features across an image

Usage: 
feature_cascade.py filename xstep ystep size

Output:
One line for each image position of the form:
x y size class
where class is 1 or 0 indicating object presence.
'''

import sys
sys.path.append('../detection')

import glob
from lxml import etree
import cv
import os
import copy
import sys
import cascadedetect


if __name__=='__main__':

    imagefilename = sys.argv[1]
    xstep = int(sys.argv[2])
    ystep = int(sys.argv[3])
    size = int(sys.argv[4])

    matchingcoords = cascadedetect.detect(imagefilename,cascadefile='../../data/cascade/cascade_HAAR2.xml',
                                          trainpatchsize=14,smallestobjectsize=45.0,scalefactor=1.1,minneighbours=1)         
    im = cv.LoadImage(imagefilename)

    # Scan through patch locations in the image
    width = im.width
    height = im.height
    x = xstep
    y = ystep
    while y<height:
        x = xstep;
        while (x<width):
            # Test whether a square at this point includes the center of a detected object
            objecthere = 0
            for c in matchingcoords:
                if (x-size/2 < c[0]) and (x+size/2 > c[0]) and (y-size/2 < c[1]) and (y+size/2 > c[1]):
                    objecthere = 1
            # Output the details for this patch
            print "%d %d %d %d" % (x,y,size,objecthere)
            x+=xstep;
        y += ystep;

