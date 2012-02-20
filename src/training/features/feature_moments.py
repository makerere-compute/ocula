#!/usr/bin/python
'''
Calculate contour features across an image

Usage: 
feature_contour.py filename xstep ystep size

Output:
One line for each image position of the form:
x y size class
where class is 1 or 0 indicating object presence.
'''

import glob
from lxml import etree
import cv
import os
import copy
import sys


if __name__=='__main__':
    scale = 0.2
    imagefilename = sys.argv[1]
    xstep = int(round(int(sys.argv[2]) * scale))
    ystep = int(round(int(sys.argv[3]) * scale))
    size = int(round(int(sys.argv[4]) * scale))

    # get the edge image
    imcolourbig = cv.LoadImage(imagefilename)
    imcolour = cv.CreateImage((int(imcolourbig.width*scale),int(imcolourbig.height*scale)),cv.IPL_DEPTH_8U,3)
    cv.Resize(imcolourbig,imcolour)
    imgray = cv.CreateImage(cv.GetSize(imcolour),8,1)
    imedge = cv.CreateImage(cv.GetSize(imcolour),8,1)
    imedge2 = cv.CreateImage(cv.GetSize(imcolour),8,1)
    cv.CvtColor(imcolour,imgray,cv.CV_RGB2GRAY)
    cv.Canny(imgray, imedge, 10, 30)
    cv.Canny(imgray, imedge2, 10, 30)
    storage_contours = cv.CreateMemStorage()
    storage_convexhull = cv.CreateMemStorage()

    ''' 
    cv.NamedWindow("tmp1", 1)
    cv.NamedWindow("tmp2", 1)
    cv.ShowImage("tmp1", imcolour)
    cv.ShowImage("tmp2", imedge)
    '''

    # Scan through patch locations in the image
    width = imgray.width
    height = imgray.height
    x = xstep
    y = ystep
    while y<height:
        x = xstep;
        while (x<width):

            # Get contour features for this patch
            cv.SetImageROI(imedge,(x-(size/2),y-(size/2),size,size))
            #contours = cv.FindContours(imedge, storage_contours, mode=cv.CV_RETR_LIST);
            #mat = cv.CreateMat(size, size, cv.CV_8U)
            mat = imedge2[y-(size/2):y+(size/2),x-(size/2):x+(size/2)]
            #for i in range(size):
            #    for j in range(size):
            #        mat[i,j]=imedge[i,j]

            m = cv.Moments(mat,binary=1)
            #cv.ShowImage("tmp2", imedge)
            #cv.WaitKey(0)
            #print m.m00
            p = cv.GetHuMoments(m)
            #if contours and len(contours)>3:
            #convexhull = cv.ConvexHull(contours,storage_convexhull)

            # Output the details for this patch
            #print int(x/scale),int(y/scale),int(size/scale),p[0],p[1],p[2],p[3],p[4],p[5],p[6]
            #print int(x/scale),int(y/scale),int(size/scale),m.m00 #m.mu02 #,m.mu03,m.mu11,m.mu12,m.mu20,m.mu21,m.mu30
            #print int(x/scale),int(y/scale),int(size/scale),m.m00,m.m20,m.mu02,m.m11,m.mu03,m.mu11,m.mu12,m.mu20,m.mu21,m.mu30
            print int(round(x/scale)),int(round(y/scale)),int(round(size/scale)),m.m00,m.m20,m.mu02,m.m11,m.mu03,m.mu11,m.mu12,m.mu20,m.mu21,m.mu30,p[0],p[1],p[2],p[3],p[4],p[5],p[6]

            x+=xstep;
        y += ystep;

