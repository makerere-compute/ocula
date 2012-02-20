#!/usr/bin/python
"""
Use a classifier cascade to identify matches in a given image.
"""
import cv2
import cv2.cv as cv

def detect(imagefilename,cascadefile='../../data/cascade/cascade_HAAR2.xml',trainpatchsize=14,smallestobjectsize=45.0,scalefactor=1.1,minneighbours=2):
    cascade = cv2.CascadeClassifier()
    cascade.load(cascadefile)
    img = cv2.imread(imagefilename)
    imagescale = trainpatchsize/smallestobjectsize
    if imagescale!=1:
        width = img.shape[0]
        height = img.shape[1]
        img = cv2.resize(img,(int(height*imagescale),int(width*imagescale)))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = cascade.detectMultiScale(gray, scaleFactor=scalefactor, minNeighbors=minneighbours, minSize=(trainpatchsize,trainpatchsize), maxSize=(int(trainpatchsize*(scalefactor**2))+1,int(trainpatchsize*(scalefactor**2))+1))
    if len(rects) == 0:
        return []
    matches = []
    for r in rects:
        matches.append((int((1/imagescale)*(r[0]+r[2]/2)),int((1/imagescale)*(r[1]+r[3]/2))))

    return matches
