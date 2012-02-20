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

import glob
from lxml import etree
import cv
import os
import copy
import sys
import cascadedetect
import boosteddetect


if __name__=='__main__':
    imagefilename = sys.argv[1]
    xstep = int(sys.argv[2])
    ystep = int(sys.argv[3])
    size = int(sys.argv[4])
    detectortype = sys.argv[5] 

    if detectortype=='cascade':
        matchingcoords = cascadedetect.detect(imagefilename)
    elif detectortype=='boost-surf':
        patchscores = boosteddetect.detect(imagefilename,featuretype='surf',returnpatchscores=True)
    elif detectortype=='boost-moments':
        patchscores = boosteddetect.detect(imagefilename,featuretype='moments',returnpatchscores=True)

    im = cv.LoadImage(imagefilename)

    # Scan through patch locations in the image
    patchidx = 0
    width = im.width
    height = im.height
    x = xstep
    y = ystep
    while y<height:
        x = xstep;
        while (x<width):
            # Test whether a square at this point includes the center of a detected object
            if detectortype=='cascade':
                objecthere = 0
                for c in matchingcoords:
                    cx = c[0]
                    cy = c[1]
                    #cv.Circle( im, (cx,cy), 20, [255,0,0])
                    # Detected object within area unique to current patch
                    if (cx<(x+xstep-size/2.0) and
                       cx>(x-size/2.0) and
                       cy<(y+ystep-size/2.0) and
                       cy>(y-size/2.0)):

                    # Detected object anywhere within current patch   
                    #if (x-size/2 < c[0]) and (x+size/2 > c[0]) and (y-size/2 < c[1]) and (y+size/2 > c[1]):
                        #cv.Rectangle(im,(x-size/2,y-size/2),(x+size/2,y+size/2), [0, 255, 0])
                        objecthere = 1
                        break
    
                # Output the details for this patch
                print "%d %d %d %d" % (x,y,size,objecthere)
            else:
                score = patchscores[patchidx]
                patchidx+=1
                print "%d %d %d %.4f" % (x,y,size,score)
            x+=xstep;
        y += ystep;
    '''
    cv.NamedWindow('result', 1)
    cv.ShowImage('result',im)
    cv.WaitKey(0)
    '''

