/*
Calculate feature descriptors at regular positions on a grid

Usage:
densedescriptors imagefilename featuretype xstep ystep size

featuretype = [surf|sift|brief|orb]

Output:
One line for each descriptor of the form:
x y size d1 d2 d3... d64
where d1 ... d64 are the SIFT descriptor values.

Compile with:
g++ `pkg-config --cflags opencv` -lopencv_core -lopencv_features2d -o feature_densedescriptors feature_densedescriptors.cpp
*/
#include <stdio.h>
#include "opencv2/core/core.hpp"
#include "opencv2/features2d/features2d.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <iostream>
#include <vector>
#include <stdio.h>

using namespace cv;

int main(int argc, char** argv)
{
    const char* filename = argv[1];
    const char* featuretype = argv[2];
    int xstep;
    int ystep;
    int width;
    int height;
    int size;
    float scale;
    int extended;
    int x=0;
    int y=0;
    sscanf(argv[3], "%d", &xstep);
    sscanf(argv[4], "%d", &ystep);
    sscanf(argv[5], "%d", &size);
 
    IplImage* image;
    if (strcmp(featuretype,"OpponentSURF")==0 || strcmp(featuretype,"OpponentSIFT")==0) {
        image = cvLoadImage(filename);
    }
    else {
        image = cvLoadImage(filename, CV_LOAD_IMAGE_GRAYSCALE );
    }

    vector<KeyPoint> keypoints;

    width=image->width;
    height=image->height;
    y = ystep;
    while (y<height) {
        x = xstep;
        while (x<width) {
            KeyPoint point = KeyPoint(x, y, size);
            keypoints.push_back(point);
            x+=xstep;
        }
        y += ystep;
    }

    Ptr<DescriptorExtractor> extractor =  DescriptorExtractor::create(featuretype);

	Mat descriptors;
	extractor->compute(image, keypoints, descriptors);

    int ndescriptors, descriptorsize;
    ndescriptors = descriptors.rows;
    descriptorsize = descriptors.cols;
    //printf("Descriptor size %d\n",descriptorsize);

    int kpx, kpy, kpx_old, kpy_old, missingpoints, i, foundkeypoint;
    kpx_old = -1;
    kpy_old = -1;
    i = 0;
    y = ystep;
    while (y<height) {
        x = xstep;
        while (x<width) {

            kpx = int(keypoints[i].pt.x);
            kpy = int(keypoints[i].pt.y);

            // if there is a missing line, fill it in
            if ((kpx>x && kpy==y) || kpy>y) {
                printf("%d %d %d ",x,y,size);
                for (int j=0;j<descriptorsize;j++) {
                    printf("0 ");
                }
                printf("\n");
            }
            else {
                // if this is not a duplicate, output the descriptor
                foundkeypoint = 0;
                while (foundkeypoint==0) {
                    if (x==kpx && y==kpy) {
                        printf("%d %d %d ", int(keypoints[i].pt.x),int(keypoints[i].pt.y),size);
                        for (int j=0;j<descriptorsize;j++) {
                            if (strcmp(featuretype,"SURF")==0) {
                                printf("%.5f ",descriptors.at<float>(i,j));
                            }
                            else if (strcmp(featuretype,"ORB")==0) {
                                printf("%u ",descriptors.at<uchar>(i,j));
                            }
                            else {
                                printf("%.0f ",descriptors.at<float>(i,j));
                            }
                        }
                        printf("\n");
                        foundkeypoint = 1;
                    }
                    i++;
                    kpx = int(keypoints[i].pt.x);
                    kpy = int(keypoints[i].pt.y);
                }
            }
            x+=xstep;
        }
        y += ystep;
    }

    cvReleaseImage( &image );
}

