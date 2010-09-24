# Provides an interface for a webcam, particularly aimed for low light
# conditions in microscopy. Properties such as brightness and contrast
# can be adjusted, frames can be integrated to cancel noise, and the
# magnification of the microscope can be specified to give a length scale
# on the screen.
#
# To use: 

import cv
import numpy
import fnmatch
import os

# Get the capture interface to the camera
capture = cv.CaptureFromCAM(0)

IMAGE_FILE_PREFIX = 'scope'
SAVE_IMAGE_DIR = './savedimages/'
N_DIGITS_IN_FILE_ID = 3

global _N_INIT_STACK_FRAMES
_N_INIT_STACK_FRAMES = 100

global magnification
magnification = 40

def on_brightness_trackbar (position):
    brightness = position/100.0
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_BRIGHTNESS,brightness)

def on_contrast_trackbar (position):
    contrast = position/100.0
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_CONTRAST,contrast)

def on_magnification_trackbar (position):
    obs = (4, 10, 40, 63)
    global magnification
    magnification = obs[position]

def on_integration_trackbar (position):
    global _N_INIT_STACK_FRAMES
    _N_INIT_STACK_FRAMES = position

def save_image(img):
    """
    save to the image directory, with an incremented id number
    """
    # Note when saving, pixel values should be in the range 0-255
    ids = [-1]
    # Get the next sequential id number so nothing is overwritten
    for file in os.listdir(SAVE_IMAGE_DIR):
        if fnmatch.fnmatch(file, IMAGE_FILE_PREFIX+'*'):
            id = int(file[len(IMAGE_FILE_PREFIX):len(IMAGE_FILE_PREFIX)+4])
            ids.append(id)
    newid = max(ids) + 1
    filename = '%s%s%.4d.png' % (SAVE_IMAGE_DIR,IMAGE_FILE_PREFIX,newid)
    cv.SaveImage(filename,img)
    print('Saved image %s' % filename)
            
def stack_and_save():
    """
    integrate a number of frames to cancel sensor noise in low light, then save file
    """
    print('Integrating %d frames...' % _N_INIT_STACK_FRAMES)
    framelist = []
    I = numpy.zeros((480,640,3),dtype='float32')
    
    for i in range(0,_N_INIT_STACK_FRAMES):
        img = cv.QueryFrame(capture)
        # Use numpy to do numerical manipulation
        imgarr =  numpy.cast['float32'](numpy.asarray(cv.GetMat(img)))
        if len(I)==0:
            I = imgarr
        else:
            I = I + imgarr
        cv.ShowImage("camera", img)
        cv.WaitKey(10)

    # Normalise so the max value is 1
    I[:,:,0] = I[:,:,0]/float(I[:,:,0].max())
    I[:,:,1] = I[:,:,1]/float(I[:,:,1].max())
    I[:,:,2] = I[:,:,2]/float(I[:,:,2].max())

    drawscale(I)
    save_image(I*255)
    cv.ShowImage("camera", I)

    # Wait for a key to be pressed before continuing
    cv.WaitKey(-1)

def drawscale(img):
    """
    draws a length scale on the screen
    """
    font = cv.InitFont(0,.5,.5)
    pt1 = (20,20)
    textcolour = (0,0,0)
    cv.PutText(img,'x%d obj' % magnification,pt1,font,textcolour)

    width = 2.75 * magnification;
    startpt = (20,30)
    endpt = (20 + width,30)
    cv.Line(img,startpt,endpt,textcolour)   

if __name__ == '__main__':

    cv.NamedWindow("camera", 1)

    try:
	# Get capture properties and display controls on screen
        init_brightness = int(100*cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_BRIGHTNESS))
        cv.CreateTrackbar ("brightness", "camera", init_brightness, 100, on_brightness_trackbar)
        init_contrast = int(100*cv.GetCaptureProperty(capture,cv.CV_CAP_PROP_CONTRAST))
        cv.CreateTrackbar ("contrast", "camera", init_contrast, 100, on_contrast_trackbar)
        cv.CreateTrackbar ("objective lens", "camera", 1, 3, on_magnification_trackbar)
        cv.CreateTrackbar ("#frames to integrate", "camera", _N_INIT_STACK_FRAMES, 200, on_integration_trackbar)
   
	# Start the maginification scale display at a default value
        on_magnification_trackbar(1)
    
	# Capture frames and display them
        while True:
            img = cv.QueryFrame(capture)
            drawscale(img)
            cv.ShowImage("camera", img)
            key = cv.WaitKey(10)
            # Check for enter key press
            if key == 10:
                save_image(img)
            # Check for space key press
            if key == 32: 
                stack_and_save()
    except:
        print "Encoutered a problem - probably had trouble finding a camera."    
