'''
Script to learn SURF features corresponding to parasites and background.
Produce an output of the mean parasite descriptor and inverse variance of
each descriptor element for distance-based classification.
'''

import glob
from lxml import etree
import cv
import numpy

if __name__=='__main__':

    # whether to look at the images and keypoints as they are processed
    view_train_images = False
    
    # Directory containing marked up images
    source_dir = '../../data/200/'
    
    # Directory in which to create the output files
    out_dir = '../../data/'
    
    # read the list of xml annotation files
    xml_files = glob.glob(source_dir + '*.xml')
    
    if view_train_images:
        cv.NamedWindow("result", 1)
    
    backgroundfeatures = []
    parasitefeatures = []
    
    for annofile in xml_files:
        # load a copy of the image which will have objects covered up
        image = cv.LoadImageM(annofile[:-3] + 'jpg', cv.CV_LOAD_IMAGE_GRAYSCALE)
    
        # extract the bounding boxes from xml
        tree = etree.parse(annofile)
        
        r = tree.xpath('//bndbox')
        infoline = ''
        nobjects = 0
    
        # filenames for output
        imgfile = annofile[len(out_dir):-3] + 'jpg'
        backgroundfile = 'negative_' + annofile[len(source_dir):-3] + 'jpg'
            
        coords = ''
        boundingboxes = []
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
                    
                    boundingboxes.append((xmin,xmax,ymin,ymax))
                    
                    # draw a box around this area.
                    if view_train_images:
                        cv.Rectangle(image,(xmin,ymin),(xmax,ymax), [255, 255, 255], 1)
    
        # Extract all keypoints from the image
        (keypoints, descriptors) = cv.ExtractSURF(image, None, cv.CreateMemStorage(), (0, 500, 2, 2))
    
        # sort keypoints according to class
        for i in range(len(keypoints)):
            k = keypoints[i]
            # keypoint coords
            xkey = k[0][0]
            ykey = k[0][1]
            inboundingbox = False
            for b in boundingboxes:
                xmin = b[0]
                xmax = b[1]
                ymin = b[2]
                ymax = b[3]
                if xkey>xmin and xkey<xmax and ykey>ymin and ykey<ymax:
                    inboundingbox = True
                    break                
    
            if inboundingbox: 
                backgroundfeatures.append(descriptors[i])
                if view_train_images:
                    cv.Circle(image,k[0],k[2],[255, 255, 255])
            else:
                parasitefeatures.append(descriptors[i])
                if view_train_images:
                    cv.Circle(image,k[0],k[2],[0,0,0])
            
        # let's have a look
        if view_train_images:
            cv.ShowImage('result',image)
            # wait for key press 
            cv.WaitKey(0)               
                
    # calculate mean and variances of each element
    P = numpy.array(parasitefeatures)
    mu = numpy.mean(P,0)
    sigma = numpy.var(P,0)
    inverse_sigma = 1/sigma
    
    # formatted output of mean and variance info
    mu_str = ''
    sigma_str = ''
    for i in range(16):   
        mu_str = '%s%e, %e, %e, %e' % (mu_str,mu[4*i+0],mu[4*i+1],mu[4*i+2],mu[4*i+3])
        sigma_str = '%s%e, %e, %e, %e' % (sigma_str,inverse_sigma[4*i+0],inverse_sigma[4*i+1],inverse_sigma[4*i+2],inverse_sigma[4*i+3])
        if i<15:
            mu_str = '%s,\n' % (mu_str)
            sigma_str = '%s,\n' % (sigma_str)          
    print 'mu = [' + mu_str + ']\n'
    print 'inverse_sigma = [' + sigma_str + ']\n'
    
    
        

