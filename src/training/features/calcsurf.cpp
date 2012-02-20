/*
Calculate SURF descriptor for a single, specified keypoint

Compile with:
g++ `pkg-config --cflags opencv` -lopencv_core -lopencv_features2d -o calcsurf calcsurf.cpp
*/
#include <opencv2/objdetect/objdetect.hpp>
#include <opencv2/features2d/features2d.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/calib3d/calib3d.hpp>
#include <opencv2/imgproc/imgproc_c.h>

#include <iostream>
#include <vector>

int main(int argc, char** argv)
{
    const char* filename = argv[1];
    int x;
    int y;
    int size;
    sscanf(argv[2], "%d", &x);
    sscanf(argv[3], "%d", &y);
    sscanf(argv[4], "%d", &size);
    
    int SURF_EXTENDED = 0;
    int SURF_HESSIAN_THRESHOLD = 500;
    int SURF_NOCTAVES = 2;
    int SURF_NOCTAVELAYERS = 2; 
    int MATCH_THRESHOLD = 20;  

    CvSURFParams params = cvSURFParams(SURF_HESSIAN_THRESHOLD, SURF_EXTENDED);
    params.nOctaves=SURF_NOCTAVES;
    params.nOctaveLayers=SURF_NOCTAVELAYERS;
    CvMemStorage* storage = cvCreateMemStorage(0);
    IplImage* image = cvLoadImage(filename, CV_LOAD_IMAGE_GRAYSCALE );
    CvSeq *objectKeypoints = 0, *objectDescriptors = 0;

    // set up the keypoint
    int useProvidedKeyPoints = 1;
    CvMemStorage* kp_storage = cvCreateMemStorage(0);
    CvSeq* surf_kp = cvCreateSeq(0, sizeof(CvSeq), sizeof(CvSURFPoint), kp_storage);
    int laplacian = 1; 
    int direction = 0; 
    int hessian = SURF_HESSIAN_THRESHOLD+1; 
    CvSURFPoint point = cvSURFPoint(cvPoint2D32f(x, y), laplacian, size, direction, hessian);
    cvSeqPush(surf_kp, &point);

    // extract descriptor
    cvExtractSURF(image, 0, &surf_kp, &objectDescriptors, storage, params, useProvidedKeyPoints);

    // print to stdout
    /*
    // if keypoint info also wanted
    CvSeqReader kp_reader;
    cvStartReadSeq(surf_kp, &kp_reader);
    const CvSURFPoint* kp = (const CvSURFPoint*)kp_reader.ptr;
    printf("%.2f %.2f %.2f %d %d",kp->pt.x,kp->pt.y,kp->hessian,kp->laplacian,kp->size);
    */
    
    const float* des = (const float*)cvGetSeqElem(objectDescriptors, 0);
    for (int i=0;i<64;i++){
        printf("%.5f ",des[i]);
    } 
    cvReleaseImage( &image );
}

