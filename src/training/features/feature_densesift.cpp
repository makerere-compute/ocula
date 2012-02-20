/*
Calculate SIFT descriptor at regular positions on a grid

Usage:
densesurf imagefilename xstep ystep size

Output:
One line for each descriptor of the form:
x y size d1 d2 d3... d64
where d1 ... d64 are the SIFT descriptor values.

Compile with:
g++ `pkg-config --cflags opencv` -lopencv_core -lopencv_features2d -o feature_densesift feature_densesift.cpp
*/

#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/features2d/features2d.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/calib3d/calib3d.hpp>
#include <opencv2/imgproc/imgproc_c.h>

#include <iostream>
#include <vector>
#include <stdio.h>

int main(int argc, char** argv)
{
    const char* filename = argv[1];
    int xstep;
    int ystep;
    int width;
    int height;
    int size;
    float scale;
    int extended;
    int x=0;
    int y=0;
    sscanf(argv[2], "%d", &xstep);
    sscanf(argv[3], "%d", &ystep);
    sscanf(argv[4], "%d", &size);
    sscanf(argv[5], "%f", &scale);
    sscanf(argv[6], "%d", &extended);
    
    int SURF_HESSIAN_THRESHOLD = 500;
    int SURF_NOCTAVES = 2;
    int SURF_NOCTAVELAYERS = 2; 
    int MATCH_THRESHOLD = 20;  

    CvSURFParams params = cvSURFParams(SURF_HESSIAN_THRESHOLD, extended);
    params.nOctaves=SURF_NOCTAVES;
    params.nOctaveLayers=SURF_NOCTAVELAYERS;
    CvMemStorage* storage = cvCreateMemStorage(0);
    IplImage* image = cvLoadImage(filename, CV_LOAD_IMAGE_GRAYSCALE );
    CvSeq *objectKeypoints = 0, *objectDescriptors = 0;

    // set up the list of keypoints
    int useProvidedKeyPoints = 1;
    CvMemStorage* kp_storage = cvCreateMemStorage(0);
    CvSeq* surf_kp = cvCreateSeq(0, sizeof(CvSeq), sizeof(CvSURFPoint), kp_storage);
    int laplacian = 1; 
    int direction = 0; 
    int hessian = SURF_HESSIAN_THRESHOLD+1; 
    width=image->width;
    height=image->height;
    y = ystep;
    while (y<height) {
        x = xstep;
        while (x<width) {
            CvSURFPoint point = cvSURFPoint(cvPoint2D32f(x, y), laplacian, size, direction, hessian);
            cvSeqPush(surf_kp, &point);
            x+=xstep;
        }
        y += ystep;
    }

    // extract descriptors from the image
    cvExtractSURF(image, 0, &surf_kp, &objectDescriptors, storage, params, useProvidedKeyPoints);

    // kp->pt.x,kp->pt.y,kp->hessian,kp->laplacian,kp->size);
   
    // print out the descriptor info to stdout
    int xdim;
    if (extended==1) {
        xdim=128;
    }
    else {
        xdim=64;
    }
    const float* des;
    const CvSURFPoint* kp;
    for (int ides=0;ides<objectDescriptors->total;ides++){
        des = (const float*)cvGetSeqElem(objectDescriptors, ides);
        kp = (const CvSURFPoint*)cvGetSeqElem(surf_kp, ides);
        printf("%d %d %d ",int(kp->pt.x),int(kp->pt.y),int(kp->size));
        for (int i=0;i<xdim;i++){
            printf("%.5f ",des[i]);
        }
        printf("\n");
    }

    cvReleaseImage( &image );
}

