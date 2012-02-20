'''
Script to learn SURF features corresponding to parasites and background.
Produce an output of the mean parasite descriptor and inverse variance of
each descriptor element for distance-based classification.
'''

import glob
from lxml import etree
import cv
import numpy

def writearffline(filehandle,descriptor,cascadeoutput,descriptorclass):
    for bin in range(64):
        filehandle.write('%.4f, ' % (descriptor[bin]))
    filehandle.write('%d, %s \n' % (cascadeoutput, descriptorclass))


if __name__=='__main__':
    
    # Directory containing marked up images
    source_dir = '../../data/'
    
    # Directory in which to create the output files
    out_dir = '../../data/'
    
    # read the list of xml annotation files
    xml_files = glob.glob(source_dir + 'train-smallset/*.xml')

    # read feature files with this suffix
    featuretype = ['surf_15_30', 'cascade_15_40']

    #xml_files = glob.glob(source_dir + 'train-positive/*.xml')
    #xml_files.extend(glob.glob(source_dir + 'train-negative/*.xml'))

    # set up ARFF header
    of = open('descriptors%s.arff' % ('_'.join(featuretype)),'w')
    of.write('@relation plasmodium-%s \n\n' % ('_'.join(featuretype)))
    for i in range(64):
        of.write('@attribute bin%d real \n' % (i))
    of.write('@attribute cascadeoutput {0, 1} \n\n')
    of.write('@attribute class {positive, negative} \n\n')
    of.write('@data \n')
    
    filecounter = 1
    ### main loop ### 
    for annofile in xml_files:
        print('%d/%d' % (filecounter, len(xml_files)))
        filecounter += 1
        tree = etree.parse(annofile)
        r = tree.xpath('//bndbox')
        infoline = ''
        nobjects = 0
        coords = ''
        boundingboxes = []

        # extract the bounding boxes from xml
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
    
        # Extract all keypoints from the image
        descriptorfile = annofile[:-3] + featuretype[0]
        data = numpy.genfromtxt(descriptorfile)

        cascadeoutputfile = annofile[:-3] + featuretype[1]
        cascadedata = numpy.genfromtxt(cascadeoutputfile)

        # sort keypoints according to class
        for i in range(data.shape[0]):
            xkey = data[i,0]
            ykey = data[i,1]
            descriptor = data[i,3:]
            inboundingbox = False
            for b in boundingboxes:
                xmin = b[0]
                xmax = b[1]
                ymin = b[2]
                ymax = b[3]
                if xkey>xmin and xkey<xmax and ykey>ymin and ykey<ymax:
                    inboundingbox = True
                    break                

            # write the information to the training file    
            if inboundingbox:
                writearffline(of,descriptor,cascadedata[i,3],'positive')
            else:
                writearffline(of,descriptor,cascadedata[i,3],'negative')

    of.close()
