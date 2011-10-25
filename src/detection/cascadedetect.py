#!/usr/bin/python
"""
Use a classifier cascade to identify matches in a given image.
"""
import cv2
import cv2.cv as cv

def detectparasites(imagefilename):
    cascade = cv2.CascadeClassifier()
    cascade.load('../../data/cascade/cascade.xml')
    img = cv2.imread(imagefilename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=10, minSize=(20,20), maxSize=(40,40))
    if len(rects) == 0:
        return []
    #rects[:,2:] += rects[:,:2]
    matches = []
    for r in rects:
        matches.append((r[0]+r[2]/2,r[1]+r[3]/2))
    return matches
