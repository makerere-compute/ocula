#!/usr/bin/python
'''
Calculate the precision, recall and F-score of a particular object detection
algorithm. Usage: options 

findaccuracy.py [-s|--show] [--savepatches] 

options -s or --show display each test image, along with the ground truth, the
matches (true positives in blue, false positives in red), and a count of TP
(true positives), FP (false positives) and FN (false negatives). During image
display, press escape to quit from the image display, any other key to move to
the next image.

Without these options, the overall performance statistics are calculated with 
no images being displayed.
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
import surfdetect
import momentdetect
import boosteddetect
import naivebayesdetect
class BadImageError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getboundingboxes(imgfile):
    '''
    Given an image filename, get a list of the bounding boxes around each 
    whitefly (the ground truth locations of each whitefly).
    '''
    annofile = imgfile[:-3] + 'xml'
    annofileexists = os.path.exists(annofile)
    boundingboxes = []

    if (annofileexists):
        # Read the bounding boxes from xml annotation
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

    # Process command line options to determine whether to look at the images 
    # and keypoints as they are processed.
    show_images = False
    quick = False
    partitionmode = False
    linethickness=1
    show_circles = True
    if ('--show' in sys.argv) or ('-s' in sys.argv):
        show_images = True
    if show_images:
        cv.NamedWindow('result', 1)

    if ('--quick' in sys.argv) or ('-q' in sys.argv):
        quick = True

    if ('--partition' in sys.argv) or ('-p' in sys.argv):
        partitionmode = True
   
    # Whether to save detected region patches for further training
    save_patches = False
    if ('--savepatches' in sys.argv):
        save_patches = True
        patchid = 0

    # Directories containing test images
    dir_prefix = '../../data/'
    if partitionmode:
        partitionnumber = 0
        test_file_lists = glob.glob(dir_prefix + 'testpartition*.txt')
    else:
        #test_directories = ['train-positive']
        #test_directories = ['train-smallset']
        test_file_lists = ['test-positive','test-negative']

    # Directories in which to save image patches
    patch_directory_positive = 'train-positive-patch'
    patch_directory_negative = 'train-negative-patch'


    #for image_directory in test_directories:
    for file_list in test_file_lists:

        if partitionmode:
            partitionnumber += 1
            pfile = open(file_list,'r')
            objectprior = float(pfile.readline())
            img_files = pfile.readlines()
            for ifile in range(len(img_files)):
                img_files[ifile] = img_files[ifile].replace('\n','')
            pfile.close()
        else:
            objectprior = -1
            # Read the list of test image files
            source_dir = dir_prefix + file_list + '/'
            if quick:
                img_files = glob.glob(source_dir + '20110422_140*.jpg')
            else:
                img_files = glob.glob(source_dir + '*.jpg')
        
        filenumber = 1
        nfiles = len(img_files)
        for testfile in img_files:
            partitionstr = ''
            if partitionmode:
                partitionstr = 'partition %d ' % (partitionnumber)

            print '%s %s(%d/%d)' % (testfile,partitionstr,filenumber,nfiles)
            filenumber += 1

            ###################################################################
            # Change the following line to use a different detection routine. #
            ###################################################################
            #matchingcoords = cascadedetect.detect(testfile)
            matchingcoords = naivebayesdetect.detect(testfile,threshold=0.92,prior=objectprior)
            #matchingcoords = boosteddetect.detect(testfile,featuretype='moments',threshold=0.0)
            #matchingcoords = boosteddetect.detect(testfile,featuretype='surf',threshold=1.0)
            #matchingcoords = cascadedetect.detect(testfile,cascadefile='../../data/cascade/cascade_HAAR2.xml',trainpatchsize=14,smallestobjectsize=45.0,scalefactor=1.1,minneighbours=2)
            boundingboxes = getboundingboxes(testfile)
            im = cv.LoadImage(testfile)

            # If specified, save the patches containing detected regions for further training
            if save_patches:
                for match in matchingcoords:
                    xcentre = match[0]
                    ycentre = match[1]
                    matched = False
                    for bb in boundingboxes:
                        if (xcentre>bb[0] and xcentre<bb[1] and ycentre>bb[2] and ycentre<bb[3]):
                            matched = True
                            break

                    # Save the image region crop in the appropriate directory
                    width = 40
                    height = 40
                    cv.SetImageROI(im,(int(xcentre-width/2),int(ycentre-height/2),width,height))
                    if matched:
                        patchdir = patch_directory_positive
                    else:
                        patchdir = patch_directory_negative
                    filename = '%s%s/%.7d.jpg' % (dir_prefix, patchdir, patchid)
                    cv.SaveImage(filename,im)
                    patchid += 1

                cv.ResetImageROI(im)

            if show_images:
                for match in matchingcoords:
                    xcentre = match[0]
                    ycentre = match[1]
                    if show_circles:
                        cv.Circle( im, (int(xcentre),int(ycentre)), 20, [0,0,255], linethickness )
                
                for bb in boundingboxes:
                    cv.Rectangle(im,(bb[0],bb[2]),(bb[1],bb[3]), [255, 255, 255], linethickness)
                
            TPim = FPim = FNim = 0
            
            # Test the matches - count true positives, false positives and false negatives.
            tmpbb = copy.deepcopy(boundingboxes)  
            for match in matchingcoords:
                xcentre = match[0]
                ycentre = match[1]
                matched = False
                for bb in tmpbb:
                    # If the detected centre falls in the middle of a whitefly bounding
                    # box, then it's a true positive.
                    if (xcentre>bb[0] and xcentre<bb[1] and ycentre>bb[2] and ycentre<bb[3]):
                        TPim+=1
                        # Remove the matches bounding boxes from ground truth, so that
                        # we can only match each whitefly once.
                        tmpbb.remove(bb)
                        if show_circles:
                            cv.Circle( im, (int(xcentre),int(ycentre)), 20, [255,0,0], linethickness )
                        matched = True
                        break

                if not matched:
                    FPim+=1
                    if show_circles:
                        cv.Circle( im, (int(xcentre),int(ycentre)), 20, [0,0,255], linethickness )

            for bb in tmpbb:
                FNim+=1
                cv.Rectangle(im,(bb[0],bb[2]),(bb[1],bb[3]), [255, 255, 255], linethickness)
            
            TP += TPim
            FP += FPim
            FN += FNim
            
            if len(matchingcoords)>0:
                cv.PutText(im, 'TP=%d, FP=%d, FN=%d' % (TPim,FPim,FNim), (11,21), 
                    cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5), (0,0,0))
                cv.PutText(im, 'TP=%d, FP=%d, FN=%d' % (TPim,FPim,FNim), (11,21), 
                    cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5), (255,255,255))
    
            if show_images:
                cv.ShowImage('result', im)
    
                if cv.WaitKey(0) == 27:
                    break

        
    print('TP=%d, FP=%d, FN=%d' % (TP,FP,FN))
    precision = (TP*1.0)/(TP+FP)
    recall = (TP*1.0)/(TP+FN)
    fscore = 2*precision*recall/(precision+recall)
    print('Precision=%.3f, Recall=%.3f, F-score=%.3f' % (precision,recall,fscore))
    
