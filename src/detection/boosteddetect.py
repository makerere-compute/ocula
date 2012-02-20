'''
Use dense SURF features to identify matches in a given image
'''

import cv2
import numpy
import scipy.stats
import pickle



def detect(imagefilename,featuretype='surf',threshold=0.0,returnpatchscores=False):
    paramsdir = '../../data/params/'
    mergepairs = True
    '''
    allclasses = numpy.loadtxt('%s/classes.txt' % (paramsdir))
    allweights = numpy.loadtxt('%s/weights.txt' % (paramsdir))
    allmeans = numpy.loadtxt('%s/means.txt' % (paramsdir))
    allcovs = numpy.loadtxt('%s/covs.txt' % (paramsdir))

    picklefile = open('../training/surfparams.pkl', 'rb')
    pickle.load(picklefile) # mu_pos
    pickle.load(picklefile) # mu_neg
    pickle.load(picklefile) # Sigma_pos
    pickle.load(picklefile) # Sigma_neg
    posnegratio = pickle.load(picklefile)
    picklefile.close()

    ncomponents = len(allweights)
    xdim = allmeans.shape[0]
    allweights[numpy.nonzero(allclasses==1)] *= posnegratio
    allweights[numpy.nonzero(allclasses==0)] *= (1-posnegratio)
    
    mixture = []
    for i in range(ncomponents):
        p = {}
        p['class'] = allclasses[i]
        p['weight'] = allweights[i]
        p['mu'] = allmeans[:,i]
        p['Sigma'] = allcovs[:,i*xdim:(i+1)*xdim]
        p['Sigma_inv'] = numpy.linalg.inv(p['Sigma'])
        p['normconstant'] = numpy.exp(-0.5*xdim*numpy.log(2*numpy.pi))*numpy.power(numpy.linalg.det(p['Sigma']),-0.5)
        mixture.append(p)
    '''
    classifier = cv2.Boost()
    #classifier = cv2.SVM()
    classifier.load('%sboost-%s-classifier.cv2' % (paramsdir,featuretype))
    # load descriptors from feature file
    patchstep = 25
    patchsize = 30
    #featuretype = 'surf_%d_%d' % (patchstep,patchsize)
    featurestring = '%s_%d_%d' % (featuretype,patchstep,patchsize)
    descriptorfile = imagefilename[:-3] + featurestring
    data = numpy.genfromtxt(descriptorfile)

    # for each descriptor, determine whether there is a match or not
    matches = []
    for i in range(data.shape[0]):
        xkey = data[i,0]
        ykey = data[i,1]
        descriptor = numpy.array(data[i,3:],dtype=numpy.float32)
        p = classifier.predict(descriptor, returnSum=True)
        #p = classifier.predict(descriptor, returnDFVal=True)
        if returnpatchscores:
            matches.append(p)
        elif p>threshold:
            if (not mergepairs) or (((xkey-patchstep,ykey) not in matches) and ((xkey,ykey-patchstep) not in matches)):
                matches.append((xkey,ykey))
    return matches
