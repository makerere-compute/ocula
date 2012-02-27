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

def printsummarystats(positivedescriptors,negativedescriptors,poscount,negcount):
    mu_pos = numpy.mean(positivedescriptors,0)
    mu_neg = numpy.mean(negativedescriptors,0)
    Sigma_pos = numpy.cov(positivedescriptors,None,0)
    Sigma_neg = numpy.cov(negativedescriptors,None,0)
    posnegratio = (1.0*poscount)/negcount

    output = open('../../data/params/momentparams.pkl', 'wb')
    pickle.dump(mu_pos, output)
    pickle.dump(mu_neg, output)
    pickle.dump(Sigma_pos, output)
    pickle.dump(Sigma_neg, output)
    pickle.dump(posnegratio, output)
    output.close()
    numpy.savetxt('negmoments.csv',negativedescriptors)
    numpy.savetxt('posmoments.csv',positivedescriptors)

def trainclassifier(positivedescriptors,negativedescriptors,poscount,negcount,featurename):
    # Set up training data structures
    xdim = negativedescriptors.shape[1]
    npos = positivedescriptors.shape[0]
    nneg = negativedescriptors.shape[0]
    train_data = numpy.zeros((npos+nneg,xdim),dtype=numpy.float32)
    train_data[0:npos,:] = positivedescriptors[0:npos,:]
    train_data[npos:(npos+nneg),:] = negativedescriptors[0:nneg,:]
    responses = numpy.zeros(npos+nneg,dtype=numpy.float32)
    responses[0:npos]=1
    responses[npos:(npos+nneg)]=-1
    # Carry out the training
    params = dict(weak_count = 200, weight_trim_rate = 0.99, cv_folds = 10, max_depth = 2)
    classifier = cv2.Boost(train_data,cv2.CV_ROW_SAMPLE,responses, params = params)
    # Save the classifier
    classifierfilename = '../../data/params/boost-%s-classifier.cv2' % (featurename)
    classifier.save(classifierfilename)
    print('Classifier saved to %s' % (classifierfilename))

if __name__=='__main__':
    # Directory containing marked up images
    source_dir = '../../data/'
    
    # Read feature files with this suffix
    patchstep = 25
    patchsize = 30
    #featurename = 'surf'
    #featurename = 'sift'
    featurename = 'orb'
    #featurename = 'moments'
    featuretype = '%s_%d_%d' % (featurename,patchstep,patchsize)
    traintargetssuffix = 'traintargets_%d_%d' % (patchstep,patchsize)

    quick = False
    if quick:
        feature_files = glob.glob(source_dir + 'train-positive/20110422_14*.%s' % (featuretype))
        nposdescriptorstouse = 2400 
        nnegdescriptorstouse = 20000
    else:
        feature_files = glob.glob(source_dir + 'train-positive/*.%s' % (featuretype))
        nposdescriptorstouse = 32593
        nnegdescriptorstouse = 200000


    #feature_files.extend(glob.glob(source_dir + 'train-negative/*.%s' % (featuretype)))
    #feature_files = glob.glob(source_dir + 'train-smallset/*.%s' % (featuretype))

    # The parameters to train
    descriptorsize = numpy.loadtxt(feature_files[0]).shape[1]-3
    negativeacceptancerate =.15 
    positivedescriptors = numpy.zeros((nposdescriptorstouse,descriptorsize),dtype=numpy.float32)
    negativedescriptors = numpy.zeros((nnegdescriptorstouse,descriptorsize),dtype=numpy.float32)
    iposdescriptor = 0
    inegdescriptor = 0
    poscount = 0
    negcount = 0

    filecounter = 1
    ### main loop ### 
    for descriptorfile in feature_files:

        #print('%d/%d' % (filecounter, len(feature_files)))
        annofile = descriptorfile[:-len(featuretype)] + 'xml'
        traintargetsfile = descriptorfile[:-len(featuretype)] + traintargetssuffix
        filecounter += 1
        tree = etree.parse(annofile)
        r = tree.xpath('//bndbox')
        infoline = ''
        nobjects = 0
        coords = ''

        # Extract all keypoints from the image
        data = numpy.loadtxt(descriptorfile)
        traintargets = numpy.loadtxt(traintargetsfile)

        # sort keypoints according to class
        for i in range(data.shape[0]):
            xkey = data[i,0]
            ykey = data[i,1]
            descriptor = data[i,3:]
            inboundingbox = traintargets[i,3]>0

            if inboundingbox:
                poscount+=1
                if iposdescriptor<nposdescriptorstouse:
                    positivedescriptors[iposdescriptor,:] = descriptor
                    iposdescriptor+=1
            else:
                negcount+=1
                if inegdescriptor<nnegdescriptorstouse and numpy.random.random()<negativeacceptancerate:
                    negativedescriptors[inegdescriptor,:] = descriptor
                    inegdescriptor+=1

            if iposdescriptor>=nposdescriptorstouse and inegdescriptor>=nnegdescriptorstouse:
                #printsummarystats(positivedescriptors,negativedescriptors,poscount,negcount)
                trainclassifier(positivedescriptors,negativedescriptors,poscount,negcount,featurename)
                exit()

        print iposdescriptor, inegdescriptor
