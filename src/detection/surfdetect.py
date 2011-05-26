'''
Given frames of a video, calculate the positions of any parasites. Optimised for
mobile computation: using SURF features, calculate Mahalanobis distance from the
mean parasite training descriptor.
'''

import cv
import numpy
import math
from time import clock
from kdtree import *

def findmatches(imageDescriptors,mu,inverse_sigma,threshold):
    '''
    For each of the keypoint descriptors, calculate whether they match the
    training examples given a mean and inverse variance of the training 
    descriptors. 
    '''
    matches= []
    
    Nkeypoints = len(imageDescriptors)
    for k in range(Nkeypoints):
        des = imageDescriptors[k]
               
        # squared Mahalanobis distance, assuming diagonal covariance
        dist = 0
        for i in range(64):
            dist += ((des[i]-mu[i])**2)*inverse_sigma[i]
        
        if dist<threshold:
            matches.append(k)
            
    return matches

if __name__ == '__main__':
    # feature extraction params
    SURF_EXTENDED = 0
    SURF_HESSIAN_THRESHOLD = 500
    SURF_NOCTAVES = 2
    SURF_NOCTAVELAYERS = 2 
    
    # parasite matching params
    MATCH_THRESHOLD = 20    
    
    # magic numbers from surftraining.py 
    mu = [5.819627e-04, -1.362842e-03, 2.391441e-03, 2.645388e-03,
    1.736164e-02, -1.230714e-02, 2.497016e-02, 1.932175e-02,
    1.357752e-02, -5.328481e-03, 1.746906e-02, 1.109308e-02,
    4.588704e-04, 1.048637e-04, 9.707647e-04, 8.380755e-04,
    1.770340e-03, -4.429551e-03, 1.501682e-02, 1.513996e-02,
    -4.374340e-04, -1.287441e-01, 2.782514e-01, 1.948743e-01,
    2.738553e-01, -1.216200e-01, 2.884202e-01, 1.637557e-01,
    3.944878e-03, 1.265369e-03, 6.518393e-03, 5.406772e-03,
    3.621008e-03, 3.041889e-03, 1.612071e-02, 1.579410e-02,
    -1.054817e-02, 1.283805e-01, 2.812133e-01, 2.028567e-01,
    2.837351e-01, 1.170555e-01, 2.924680e-01, 1.694813e-01,
    3.927908e-03, -9.551742e-04, 6.768408e-03, 6.973732e-03,
    6.549640e-04, 2.033027e-03, 2.435575e-03, 2.853759e-03,
    1.458403e-02, 1.152258e-02, 2.540248e-02, 2.062079e-02,
    1.357735e-02, 1.539471e-03, 1.763335e-02, 1.248309e-02,
    7.774467e-04, -6.445289e-04, 1.358011e-03, 1.293342e-03]
    
    inverse_sigma = [6.801185e+04, 6.588168e+04, 9.711188e+04, 8.665568e+04,
    1.158875e+03, 2.371370e+03, 1.567239e+03, 3.626427e+03,
    2.683483e+03, 5.881650e+03, 3.250738e+03, 8.754201e+03,
    5.403449e+05, 8.249664e+05, 6.542625e+05, 8.664666e+05,
    2.302975e+03, 2.368799e+03, 3.773819e+03, 3.477313e+03,
    1.244203e+01, 6.123593e+01, 8.211791e+01, 1.743040e+02,
    7.084477e+01, 8.174691e+01, 1.041477e+02, 1.523873e+02,
    1.958434e+04, 1.445799e+04, 2.428065e+04, 1.636511e+04,
    1.742460e+03, 1.978514e+03, 2.543752e+03, 2.813858e+03,
    1.284125e+01, 5.745215e+01, 8.913852e+01, 1.617787e+02,
    1.000989e+02, 7.500543e+01, 1.201700e+02, 1.758948e+02,
    1.844502e+04, 6.310191e+03, 2.515136e+04, 7.853815e+03,
    7.065411e+04, 8.797910e+04, 9.633089e+04, 1.050358e+05,
    1.138238e+03, 2.344646e+03, 1.575057e+03, 3.568681e+03,
    2.623678e+03, 4.360050e+03, 3.405330e+03, 7.129815e+03,
    1.734295e+05, 1.515146e+05, 1.806751e+05, 1.696722e+05]
    
 
    try:
        cv.NamedWindow("ParaSight", 1)
        capture = cv.CaptureFromCAM(0)
        
        while True:
            imcolour = cv.QueryFrame(capture)
            if imcolour==None:
                print('No camera input')
                break
            image = cv.CreateImage((imcolour.width,imcolour.height),cv.IPL_DEPTH_8U,1)
            cv.CvtColor(imcolour,image,cv.CV_RGB2GRAY)
        
            # extract keypoints and descriptors from this frame
            (imageKeypoints, imageDescriptors) = cv.ExtractSURF(image, None, cv.CreateMemStorage(), (SURF_EXTENDED, SURF_HESSIAN_THRESHOLD, SURF_NOCTAVES, SURF_NOCTAVELAYERS))
            
            # find keypoints which match the prototype
            ptpairs = []
            if len(imageDescriptors)>0:
                matches = findmatches(imageDescriptors,mu,inverse_sigma,MATCH_THRESHOLD)
           
                for match in matches:
                    xcentre = imageKeypoints[match][0][0]
                    ycentre = imageKeypoints[match][0][1]
                    cv.Circle( imcolour, (xcentre,ycentre), 30, [0,0,255] )
                    
            if len(matches)>0:
                cv.PutText(imcolour, 'parasites detected', (10,20), cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5), (255,255,255))
            cv.ShowImage("ParaSight", imcolour)
    
            # quit if escape key is pressed
            if cv.WaitKey(10) == 27:
                break
    finally:
        capture = None
        cv.DestroyWindow("ParaSight")


