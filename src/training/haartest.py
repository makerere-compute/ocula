#!/usr/bin/python
"""
Use a haar classifier cascade to identify matches in a given image.
"""
import cv

min_size = (20, 20)
max_size = (80, 80)
image_scale = 1
haar_scale = 1.1
min_neighbors = 2
haar_flags = 0

def detect_and_draw(img, cascade):
    # allocate temporary images
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / image_scale),
			       cv.Round (img.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

    cv.EqualizeHist(small_img, small_img)

    if(cascade):
        objects = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors, haar_flags, min_size)
        if objects:
            for ((x, y, w, h), n) in objects:
                # the input to cv.HaarDetectObjects was resized, so scale the 
                # bounding box of each object and convert it to two points
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))

                # check the diagonal of the bounding box is within max_size    
                if w*image_scale<max_size[0] and h*image_scale<max_size[1] :
                    cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)

    cv.ShowImage("result", img)

if __name__ == '__main__':

    cascade = cv.Load('../../data/haarcascade_plasmodium.xml')
    cv.NamedWindow("result", 1)

    # Processing a single image
    testimage = '../../data/200/20110324_163112.jpg'
    image = cv.LoadImage(testimage, 1)
    detect_and_draw(image, cascade)
    cv.WaitKey(0)

    '''
    # Processing video
    capture = cv.CaptureFromFile('/home/jq/data/video/scope_recording_mar24.avi')
    while True:
        img = cv.QueryFrame(capture)
        if img==None or cv.WaitKey(10) == 27:
            break
        detect_and_draw(img, cascade)

    cv.DestroyWindow("result")
    '''
