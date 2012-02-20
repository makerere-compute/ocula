'''
Use dense SURF features to identify matches in a given image
'''

import cv
import numpy
import scipy.stats
import pickle

def normpdf(x,params):
    dev = x-params['mu']
    exppart = numpy.exp(-0.5*numpy.dot(numpy.dot(dev.transpose(),params['Sigma_inv']),dev))
    dmvnorm = params['normconstant']*exppart
    return dmvnorm

def matchprobability(d,mixture):
    ncomponents = len(mixture)
    odds = numpy.zeros(ncomponents)
    oddspositive=0
    oddsnegative=0
    for m in range(ncomponents):
        odds = mixture[m]['weight'] *  normpdf(d,mixture[m])
        if mixture[m]['class']==1:
            oddspositive+=odds
        else:
            oddsnegative+=odds
    posterior = oddspositive/(oddspositive+oddsnegative)
    return posterior

def detect(imagefilename):
    paramsdir = '../../data/params/'
    mergepairs = True
    allclasses = numpy.loadtxt('%s/moments_classes.txt' % (paramsdir))
    allweights = numpy.loadtxt('%s/moments_weights.txt' % (paramsdir))
    allmeans = numpy.loadtxt('%s/moments_means.txt' % (paramsdir))
    allcovs = numpy.loadtxt('%s/moments_covs.txt' % (paramsdir))

    picklefile = open('%s/momentparams.pkl' % (paramsdir), 'rb')
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

    # load descriptors from feature file
    patchstep = 25
    patchsize = 30
    featuretype = 'moments_%d_%d' % (patchstep,patchsize)
    descriptorfile = imagefilename[:-3] + featuretype
    data = numpy.genfromtxt(descriptorfile)

    # for each descriptor, determine whether there is a match or not
    matches = []
    for i in range(data.shape[0]):
        xkey = data[i,0]
        ykey = data[i,1]
        descriptor = data[i,3:]
        if descriptor[0]>0:
            p = matchprobability(descriptor,mixture)
            if p>0.5:
                if (not mergepairs) or ((xkey-patchstep,ykey) not in matches) and ((xkey,ykey-patchstep) not in matches):
                    matches.append((xkey,ykey))
    return matches
