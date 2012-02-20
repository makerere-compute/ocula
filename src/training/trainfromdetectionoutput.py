'''
Script to learn SURF features corresponding to parasites and background.
Produce an output of the mean parasite descriptor and inverse variance of
each descriptor element for distance-based classification.
'''

import glob
from lxml import etree
import cv
import cv2
import numpy
import pickle

def normalstats(X):
    stats = {}
    xdim = X.shape[1]
    stats['type'] = 'normal'
    stats['mu'] = numpy.mean(X,0)
    stats['Sigma'] = numpy.cov(X,None,0)
    if xdim>1:
        stats['Sigma_inv'] = numpy.linalg.inv(stats['Sigma'])
        stats['normconstant'] = numpy.exp(-0.5*xdim*numpy.log(2*numpy.pi))*numpy.power(numpy.linalg.det(stats['Sigma']),-0.5)
    else:
        stats['Sigma_inv'] = 1.0/stats['Sigma']
        stats['normconstant'] = numpy.exp(-0.5*xdim*numpy.log(2*numpy.pi))*numpy.power(stats['Sigma'],-0.5)
    return stats

def binomstats(X):
    stats = {}
    stats['type'] = 'binomial'
    poscount = sum(X>0)
    stats['p'] = 1.0*poscount/len(X) 
    return stats

if __name__=='__main__':

    # Directory containing marked up images
    source_dir = '../../data/'
    
    # Read feature files with this suffix
    patchstep = 25
    patchsize = 30
    featurename = ['cascade','boost-surf','boost-moments']
    nposdescriptorstouse = 32585
    nnegdescriptorstouse = 200000
    negativeacceptancerate =.15 
    iposdescriptor = 0
    inegdescriptor = 0
    poscount = 0
    negcount = 0

    nfeatures = len(featurename)

    featuretype = []
    for i in range(nfeatures):
        featuretype.append('%s_%d_%d' % (featurename[i],patchstep,patchsize))

    feature_files = []
    for i in range(nfeatures):
        feature_files.append(glob.glob('%strain-positive/*.%s' % (source_dir,featuretype[i])))
        #feature_files.extend(glob.glob(source_dir + 'train-negative/*.%s' % (featuretype[i]))
        #feature_files = glob.glob(source_dir + 'train-smallset/*.%s' % (featuretype[i]))

    # The parameters to train
    descriptorsize = numpy.loadtxt(feature_files[0][0]).shape[1]-3

    positivedescriptors = []
    negativedescriptors = []
    for i in range(nfeatures):
        positivedescriptors.append(numpy.zeros((nposdescriptorstouse,descriptorsize),dtype=numpy.float32))
        negativedescriptors.append(numpy.zeros((nnegdescriptorstouse,descriptorsize),dtype=numpy.float32))


    ### main loop ###
    finished = False
    for fileidx in range(len(feature_files[0])):
        if finished:
            break
        #print('%d/%d' % (filecounter, len(feature_files)))
        annofile = feature_files[0][fileidx][:-len(featuretype[0])] + 'xml'
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
        data = []
        for featureidx in range(nfeatures):
            data.append(numpy.loadtxt(feature_files[featureidx][fileidx]))

        # sort keypoints according to class
        for i in range(data[0].shape[0]):
            xkey = data[0][i,0]
            ykey = data[0][i,1]
            inboundingbox = False
            for b in boundingboxes:
                xmin = b[0]
                xmax = b[1]
                ymin = b[2]
                ymax = b[3]
                bbx = (xmin+xmax)/2
                bby = (ymin+ymax)/2
                # check whether a given proportion of overlap, such that there is exactly one match
                # per patch
                #if xkey>xmin and xkey<xmax and ykey>ymin and ykey<ymax:
                if ((bbx<xkey+patchstep-patchsize/2.0) and 
                    (bbx>xkey-patchsize/2.0) and 
                    (bby<ykey+patchstep-patchsize/2.0) and 
                    (bby>ykey-patchsize/2.0)):
                    inboundingbox = True
                    break                

            if inboundingbox:
                poscount+=1
                if iposdescriptor<nposdescriptorstouse:
                    for featureidx in range(nfeatures):
                        descriptor = data[featureidx][i,3:]
                        positivedescriptors[featureidx][iposdescriptor,:] = descriptor
                    iposdescriptor+=1
            else:
                negcount+=1
                if inegdescriptor<nnegdescriptorstouse and numpy.random.random()<negativeacceptancerate:
                    for featureidx in range(nfeatures):
                        descriptor = data[featureidx][i,3:]
                        negativedescriptors[featureidx][inegdescriptor,:] = descriptor
                    inegdescriptor+=1

            if iposdescriptor>=nposdescriptorstouse and inegdescriptor>=nnegdescriptorstouse:
                p = {}
                p['posnegratio'] = (1.0*poscount)/(poscount+negcount)

                for featureidx in range(nfeatures):
                    if featurename[featureidx]=='cascade':
                        posstats = binomstats(positivedescriptors[featureidx])
                        negstats = binomstats(negativedescriptors[featureidx])
                    else:
                        posstats = normalstats(positivedescriptors[featureidx]) 
                        negstats = normalstats(negativedescriptors[featureidx])

                    posstats['class'] = 1
                    negstats['class'] = 0
                    p[featurename[featureidx]] = []
                    p[featurename[featureidx]].append(posstats)
                    p[featurename[featureidx]].append(negstats)

                output = open('../../data/params/normalbayes-detectionoutput.pkl', 'wb')
                pickle.dump(p, output)
                output.close()
                print 'Saved classifier'

                finished=True
                break

        print iposdescriptor, inegdescriptor
