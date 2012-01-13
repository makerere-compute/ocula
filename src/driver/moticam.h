/*
 * moticam.h
 *
 *  Created on: Nov 21, 2011
 *      Author: mistaguy
 */

#ifndef MOTICAM_H_
#define MOTICAM_H_


#endif /* MOTICAM_H_ */

#define w_in_pix 320
#define h_in_pix 256
short padding = 00000;
short BM = 0x4d42;
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <signal.h>
#include <ctype.h>
#include <opencv/cv.h>
#include <opencv/cxcore.h>
#include <opencv/cvwimage.h>

#include <iostream>
#include <fstream>

struct bmp_header
{

    long size_of_file;
    long reserve;
    long offset_of_pixle_data;
    long size_of_header;
    long width;
    long hight;
    short num_of_colour_plane;
    short num_of_bit_per_pix;
    long compression;
    long size_of_pix_data;
    long h_resolution;
    long v_resolution;
    long num_of_colour_in_palette;
    long important_colours;


}
HEADER;

// pix array ///////////////////////////////////////////////////////////////////////////
// L to R //
char BGR [48] = {
254,000,000,   000,255,000, 255,000,000,   000,255,000,
000,000,255,   255,255,255, 000,000,255,   255,255,255,
000,000,255,   255,255,255, 000,000,255,   255,255,255,
000,000,255,   255,255,255, 000,000,255,   255,255,255};

int imageMatrix[w_in_pix][h_in_pix][3];
