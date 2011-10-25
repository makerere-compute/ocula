'''
Script to learn SURF features corresponding to parasites and background.
Produce an output of the mean parasite descriptor and inverse variance of
each descriptor element for distance-based classification.
'''

import sys
sys.path.append('../detection')

import cascadedetect
import glob
from lxml import etree
import cv
import os
import copy

class BadImageError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def getboundingboxes(imgfile):
    annofile = imgfile[:-3] + 'xml'
    annofileexists = os.path.exists(annofile)
    boundingboxes = []

    if (annofileexists):
        # extract the bounding boxes from xml
        tree = etree.parse(annofile)
        r = tree.xpath('//bndbox')
        
        bad = tree.xpath('//status/bad')
        badimage = (bad[0].text=='1')
        
        if badimage: 
            raise BadImageError(imgfile)

        if (len(r) != 0):
            for i in range(len(r)):
                xmin = round(float(r[i].xpath('xmin')[0].text))
                xmin = max(xmin,1)
                xmax = round(float(r[i].xpath('xmax')[0].text))
                ymin = round(float(r[i].xpath('ymin')[0].text))
                ymin = max(ymin,1)
                ymax = round(float(r[i].xpath('ymax')[0].text))
                xmin, xmax, ymin, ymax = int(xmin), int(xmax), int(ymin), int(ymax)

                boundingboxes.append((xmin,xmax,ymin,ymax))
                    
    return boundingboxes
    
    

if __name__=='__main__':

    TP = 0
    FP = 0
    TN = 0
    FN = 0

    # whether to look at the images and keypoints as they are processed
    show_images = False
    
    # Directory containing marked up images
    dir_prefix = '../../data/'
    test_directories = ['test-positive','test-negative']
    

    for image_directory in test_directories:
        
        source_dir = dir_prefix + image_directory + '/'

        # read the list of xml annotation files
        img_files = glob.glob(source_dir + '*.jpg')
        
        if show_images:
            cv.NamedWindow("result", 1)
        
        backgroundfeatures = []
        parasitefeatures = []
        
        filenumber = 1
        nfiles = len(img_files)
        for testfile in img_files:
            print '%s (%d/%d)' % (testfile,filenumber,nfiles)
            filenumber += 1
            
            boundingboxes = getboundingboxes(testfile)
            matchingcoords = cascadedetect.detectparasites(testfile)
            
            im = cv.LoadImage(testfile)
                        
            if show_images:
                for match in matchingcoords:
                    xcentre = match[0]
                    ycentre = match[1]
                    cv.Circle( im, (xcentre,ycentre), 10, [0,0,255] )
                
                for bb in boundingboxes:
                    cv.Rectangle(im,(bb[0],bb[2]),(bb[1],bb[3]), [255, 255, 255], 1)
                
            TPim = FPim = FNim = 0
            
            # test the positives
            tmpbb = copy.deepcopy(boundingboxes)  
            for match in matchingcoords:
                xcentre = match[0]
                ycentre = match[1]
                matched = False
                for bb in tmpbb:
                    if (xcentre>bb[0] and xcentre<bb[1] and ycentre>bb[2] and ycentre<bb[3]):
                        TPim+=1
                        tmpbb.remove(bb)
                        cv.Circle( im, (xcentre,ycentre), 10, [255,0,0] )
                        matched = True
                        break
                if not matched:
                    FPim+=1
                    cv.Circle( im, (xcentre,ycentre), 10, [0,0,255] )
                    
            for bb in tmpbb:
                FNim+=1
                cv.Rectangle(im,(bb[0],bb[2]),(bb[1],bb[3]), [255, 255, 255], 1)
            
            TP += TPim
            FP += FPim
            FN += FNim
            
            if len(matchingcoords)>0:
                cv.PutText(im, 'TP=%d, FP=%d, FN=%d' % (TPim,FPim,FNim), (11,21), cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5), (0,0,0))
                cv.PutText(im, 'TP=%d, FP=%d, FN=%d' % (TPim,FPim,FNim), (11,21), cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5), (255,255,255))
    
            if show_images:
                cv.ShowImage("result", im)
    
                if cv.WaitKey(0) == 27:
                    break
        
    
        print('TP=%d, FP=%d, FN=%d' % (TP,FP,FN))
        print('Precision=%.3f, Recall=%.3f' % ((TP*1.0)/(TP+FP),(TP*1.0)/(TP+FN)))
    
