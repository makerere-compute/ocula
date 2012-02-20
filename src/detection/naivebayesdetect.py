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

def matchprobability(d,stats,features):
    nfeatures = len(features)
    oddspositive = stats['posnegratio']
    oddsnegative = 1-oddspositive
    for f in features:
        for i in range(len(stats[f])):
            if stats[f][i]['type']=='normal':
                o = normpdf(d[f],stats[f][i])
            elif stats[f][i]['type']=='binomial':
                o = stats[f][i]['p']**d[f] * (1-stats[f][i]['p'])**(1-d[f])
            else:
                raise Exception('Unknown distribution type %s' % (stats[f][i]['type']))
            if True: #f=='boost-moments':
                if stats[f][i]['class']==1:
                    oddspositive *= o
                else:
                    oddsnegative *= o


    posterior = oddspositive/(oddspositive+oddsnegative)
    #print posterior
    return posterior

def detect(imagefilename,threshold=0.5,prior=-1.0):
    paramsdir = '../../data/params/'
    mergepairs = True
    stats = pickle.load(open('%snormalbayes-detectionoutput.pkl' % (paramsdir),'rb'))

    if prior>-1.0:
        stats['posnegratio'] = prior

    # load descriptors from feature file
    patchstep = 25
    patchsize = 30
    #featuretype = 'surf_%d_%d' % (patchstep,patchsize)

    data = {}
    features = []
    nfeatures = 0
    for feature in stats.keys():
        if feature != 'posnegratio':
            descriptorfile = '%s%s_%d_%d' % (imagefilename[:-3],feature,patchstep,patchsize)
            data[feature] = numpy.genfromtxt(descriptorfile)
            features.append(feature)

    # for each descriptor, determine whether there is a match or not
    matches = []
    for i in range(data[features[0]].shape[0]):
        xkey = data[features[0]][i,0]
        ykey = data[features[0]][i,1]
        descriptor = []
        descriptor = {}
        for feature in features:
            descriptor[feature] = data[feature][i,3:]
        p = matchprobability(descriptor,stats,features)
        if p>threshold:
            if (not mergepairs) or ((xkey-patchstep,ykey) not in matches) and ((xkey,ykey-patchstep) not in matches):
                matches.append((xkey,ykey))


    return matches
