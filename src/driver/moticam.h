/*
 * moticam.h
 *
 *  Created on: Nov 21, 2011
 *      Author: mistaguy
 */

#ifndef MOTICAM_H_
#define MOTICAM_H_


#endif /* MOTICAM_H_ */

#define w_in_pix 200
#define h_in_pix 200
short padding = 0x0000;
short BM = 0x4d42;

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
char BGR [3] = {0x00,0x00,0xFF};
////////////////////////////////////////////////////////////////////////////////////////


