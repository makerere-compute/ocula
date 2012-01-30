/*
 * moticam.c
 *
 *      Created on: Nov 13, 2011
 *      Author: mistaguy
 *      email:abiccel@yahoo.com
 *      position: Research Programmer at AI-DEV Makerere University
 */

#include "moticam.h"

#include <usb.h>
#if 0
#include <linux/usbdevice_fs.h>
#define LIBUSB_AUGMENT
#include "libusb_augment.h"
#endif

using namespace std;

struct usb_dev_handle *devh;

/* used to realease the device for other application to use
 *
 */
void release_usb_device(int dummy) {
	int ret;
	ret = usb_release_interface(devh, 0);
	if (!ret)
		printf("failed to release interface: %d\n", ret);
	usb_close(devh);
	if (!ret)
		printf("failed to close interface: %d\n", ret);
	exit(1);
}
/***
 * List all the linux devices on the buses and assign the pointer to moticam device if found
 */
void list_devices() {
	struct usb_bus *bus;
	for (bus = usb_get_busses(); bus; bus = bus->next) {
		struct usb_device *dev;

		for (dev = bus->devices; dev; dev = dev->next)
			printf("0x%04x 0x%04x\n", dev->descriptor.idVendor,
					dev->descriptor.idProduct);
	}
}
/***
 * find and assign the pointer to moticam device if found
 */
struct usb_device *find_device(int vendor, int product) {
	struct usb_bus *bus;

	for (bus = usb_get_busses(); bus; bus = bus->next) {
		struct usb_device *dev;

		for (dev = bus->devices; dev; dev = dev->next) {
			if (dev->descriptor.idVendor == vendor && dev->descriptor.idProduct
					== product)
				return dev;
		}
	}
	return NULL;
}
char * getHex(char *bytesIn, char *bytesOut, int len) {
	for (int i = 0; i < len; i++) {
		bytesOut[i] = 0x00080000 + bytesIn[i];
		//printf("%x", bytesOut[i]);
	}
	return bytesOut;
}
/***
 * print the message from the usb communication by converting from Hex to bytes
 */
void print_bytes(char *bytes, int len) {
	int i;
	if (len > 0) {
		for (i = 0; i < len; i++) {
			printf("%u,", bytes[i]);
		}
		/*printf("\"");
		 for (i = 0; i < len; i++) {
		 //printf("%c", isprint(bytes[i]) ? bytes[i] : '.');
		 }
		 printf("\"");*/
	}
}
char* toHexadecimal(unsigned int num) {
	int dividend, remain;
	char* result = (char*) malloc(8);
	result[0] = '0';
	result[1] = '0';
	result[2] = '0';
	result[3] = '0';
	result[4] = '0';
	result[5] = '0';
	result[6] = '0';
	result[7] = '0';

	char hexArray[16];
	hexArray[0] = '0';
	hexArray[1] = '1';
	hexArray[2] = '2';
	hexArray[3] = '3';
	hexArray[4] = '4';
	hexArray[5] = '5';
	hexArray[6] = '6';
	hexArray[7] = '7';
	hexArray[8] = '8';
	hexArray[9] = '9';
	hexArray[10] = 'A';
	hexArray[11] = 'B';
	hexArray[12] = 'C';
	hexArray[13] = 'D';
	hexArray[14] = 'E';
	hexArray[15] = 'F';
	int counter = 7;
	dividend = (int) (num / 16);
	remain = num % 16;
	result[counter--] = hexArray[remain];

	while (dividend != 0) {
		remain = dividend % 16;

		dividend = (int) dividend / 16;

		result[counter--] = hexArray[remain];

	}
	/*printf("%d,", result[0]);
	 printf("%d,", result[1]);
	 printf("%d,", result[2]);
	 printf("%d,", result[3]);
	 printf("%d,", result[4]);
	 printf("%d,", result[5]);
	 printf("%d,", result[6]);
	 printf("%d\t", result[7]);*/

	return result;
}

int* toHexadecimalBase10(unsigned int num) {
	int dividend, remain;
	char* result = (char*) malloc(1);
	result[0] = '0';
	result[1] = '0';
	result[2] = '0';
	result[3] = '0';
	result[4] = '0';
	result[5] = '0';
	result[6] = '0';
	result[7] = '0';

	int* resultInt = (int *) malloc(4 * sizeof(int));
	result[0] = 0;
	result[1] = 0;
	result[2] = 0;
	result[3] = 0;

	char hexArray[16];
	hexArray[0] = '0';
	hexArray[1] = '1';
	hexArray[2] = '2';
	hexArray[3] = '3';
	hexArray[4] = '4';
	hexArray[5] = '5';
	hexArray[6] = '6';
	hexArray[7] = '7';
	hexArray[8] = '8';
	hexArray[9] = '9';
	hexArray[10] = 'A';
	hexArray[11] = 'B';
	hexArray[12] = 'C';
	hexArray[13] = 'D';
	hexArray[14] = 'E';
	hexArray[15] = 'F';
	int counter = 7;
	dividend = (int) (num / 16);
	remain = num % 16;
	result[counter--] = hexArray[remain];

	while (dividend != 0) {
		remain = dividend % 16;

		dividend = (int) dividend / 16;

		result[counter--] = hexArray[remain];

	}
	char holder[3] = { result[0], result[1], '\0' };
	int value = strtol(holder, NULL, 16);
	resultInt[0] = value;

	char holder1[3] = { result[2], result[3], '\0' };
	int value1 = strtol(holder1, NULL, 16);
	resultInt[1] = value1;

	char holder2[3] = { result[4], result[5], '\0' };
	int value2 = strtol(holder2, NULL, 16);
	resultInt[2] = value2;

	char holder3[3] = { result[6], result[7], '\0' };
	int value3 = strtol(holder3, NULL, 16);
	resultInt[3] = value3;
	/*	printf("%d,", value);
	 printf("%d,", value1);
	 printf("%d,", value2);
	 printf("%d\t", value3);*/

	return resultInt;
}
void create_image(char *bytes, int len) {
	if (len > 0) {

		FILE *fp = fopen("img.ppm", "wb"); // b - binary mode
		(void) fprintf(fp, "P6\n%d %d\n255\n", w_in_pix, h_in_pix);
		int counter = 0;
		static unsigned char color[3], a[81920], r[81920], g[81920], b[81920];


		for(int w=0;w<256;w++)
		{
               //  b/a block
			for (int i = 0; i < 640; i++) {
				if (i % 2 == 0 || i == 0) {
					int v= bytes[counter];
					b[i] =v;

				} else

				{
					int v= bytes[counter];
					a[i] = v;

				}

				counter = counter + 1;
			}
            //  g/r block
			for (int i = 0; i < 640; i++) {
				if (i % 2 == 0 || i == 0) {
					int v= bytes[counter];
					g[i] = v;

				} else

				{
					int v= bytes[counter];
					r[i] = v;

				}

				counter = counter + 1;
			}

		}


//compose image
		counter=0;
		for(int width=0;width<320;width++)
		{


		 for(int height=0;height<256;height++)
		 {

			 int blue=bytes[counter++];

			printf("b:%u",blue);
			int green=bytes[counter++];
			 printf("g:%u",green);
            int red=bytes[counter++];
			 printf("r:%u",red);
           int alpha=bytes[counter++];
			 printf("a:%u\t,",alpha);
			 color[0]=red;
			 color[1]=green;
			 color[2]=blue;


			// int v=bytes[counter++];
			// color[0]=abs(v);
			 //v=bytes[counter++];
			// color[1]=abs(v);
			// v=bytes[counter++];
			 //color[2]=abs(v);
			// v=bytes[counter++];
			// 			 color[3]=abs(v);
			 fwrite(color, 1, 3, fp);

		 }


		}



		(void) fclose(fp);

	}

}

int main(int argc, char **argv) {
	int ret, vendor, product;
	struct usb_device *dev;
	char buf[65535], *endptr, imageBuf[0x0050000];
#if 0
	usb_urb *isourb;
	struct timeval isotv;
	char isobuf[393216];
#endif

	usb_init();
	usb_set_debug(255);
	usb_find_busses();
	usb_find_devices();

	//moticam vendor ID
	vendor = strtol("0x0634", &endptr, 16);
	if (*endptr != '\0') {
		printf("invalid vendor id\n");
		exit(1);
	}
	//moticam product ID
	product = strtol("0x3111", &endptr, 16);
	if (*endptr != '\0') {
		printf("invalid product id\n");
		exit(1);
	}

	dev = find_device(vendor, product);
	assert(dev);

	devh = usb_open(dev);
	assert(devh);

	signal(SIGTERM, release_usb_device);
	//the routines below check if we have a kernel driver.Claim the the interface for communication
	ret = usb_get_driver_np(devh, 0, buf, sizeof(buf));
	printf("usb_get_driver_np returned %d\n", ret);
	if (ret == 0) {
		printf(
				"interface 0 already claimed by driver \"%s\", attempting to detach it\n",
				buf);
		ret = usb_detach_kernel_driver_np(devh, 0);
		printf("usb_detach_kernel_driver_np returned %d\n", ret);
	}
	ret = usb_claim_interface(devh, 0);
	if (ret != 0) {
		printf("claim failed with error %d\n", ret);
		exit(1);
	}
	//set alternate settings
	ret = usb_set_altinterface(devh, 0);
	assert(ret >= 0);
	//get descriptors
	ret = usb_get_descriptor(devh, 0x0000001, 0x0000000, buf, 0x0000012);
	printf("1 get descriptor returned %d, bytes: ", ret);
	print_bytes(buf, ret);
	printf("\n");
	ret = usb_get_descriptor(devh, 0x0000002, 0x0000000, buf, 0x0000009);
	printf("2 get descriptor returned %d, bytes: ", ret);
	print_bytes(buf, ret);
	printf("\n");
	ret = usb_get_descriptor(devh, 0x0000002, 0x0000000, buf, 0x0000020);
	printf("3 get descriptor returned %d, bytes: ", ret);
	print_bytes(buf, ret);
	printf("\n");

	usleep(1 * 1000);
	ret = usb_release_interface(devh, 0);
	if (ret != 0)
		printf("failed to release interface before set_configuration: %d\n",
				ret);
	ret = usb_set_configuration(devh, 0x0000001);
	printf("5 set configuration returned %d\n", ret);
	ret = usb_claim_interface(devh, 0);
	if (ret != 0)
		printf("claim after set_configuration failed with error %d\n", ret);
	ret = usb_set_altinterface(devh, 0);
	printf("5 set alternate setting returned %d\n", ret);
	usleep(2500 * 1000);
	ret = usb_get_descriptor(devh, 0x0000003, 0x0000001, buf, 0x0000050);
	printf("6 get descriptor returned %d, bytes: ", ret);
	print_bytes(buf, ret);
	printf("\n");
	usleep(1 * 1000);

	/****
	 * Most of the functions below are vendor specific messages to Moticam
	 *
	 */
	ret
			= usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
					| USB_ENDPOINT_IN, 0xf1, 0x0000005, 0x00000ba, buf,
					0x0000002, 1000);
	print_bytes(buf, ret);
	printf("7 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret
			= usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
					| USB_ENDPOINT_IN, 0xf1, 0x0000062, 0x00000ba, buf,
					0x0000002, 1000);
	print_bytes(buf, ret);
	printf("8 set control request returned %d\n", ret);
	usleep(62 * 1000);

	ret
			= usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
					| USB_ENDPOINT_IN, 0xf1, 0x0000020, 0x00000ba, buf,
					0x0000002, 1000);
	print_bytes(buf, ret);
	printf("9 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000020, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("10 set control request returned %d\n", ret);
	usleep(3 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002d, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("11 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002b, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("12 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002e, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("13 set control request returned %d\n", ret);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002c, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("14 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000001, 0x00000ba, buf, 0x0000008,
			1000);
	print_bytes(buf, ret);
	printf("15 set control request returned %d\n", ret);
	usleep(2 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000022, 0x00000ba, buf, 0x0000004,
			1000);
	print_bytes(buf, ret);
	printf("16 set control request returned %d\n", ret);
	usleep(89 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000001, 0x00000ba, buf, 0x0000008,
			1000);
	print_bytes(buf, ret);
	printf("17 set control request returned %d\n", ret);
	usleep(2 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000022, 0x00000ba, buf, 0x0000004,
			1000);
	print_bytes(buf, ret);
	printf("18 set control request returned %d\n", ret);
	usleep(2 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000009, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("19 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002d, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("20 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002b, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("21 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002e, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("22 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x000002c, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("23 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret
			= usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
					| USB_ENDPOINT_IN, 0xf1, 0x0000020, 0x00000ba, buf,
					0x0000002, 1000);
	print_bytes(buf, ret);
	printf("24 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000020, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("25 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret
			= usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
					| USB_ENDPOINT_IN, 0xf1, 0x0000020, 0x00000ba, buf,
					0x0000002, 1000);
	print_bytes(buf, ret);
	printf("26 set control request returned %d\n", ret);
	usleep(1 * 1000);

	ret = usb_control_msg(devh, USB_RECIP_DEVICE | USB_TYPE_VENDOR
			| USB_ENDPOINT_OUT, 0xf0, 0x0000020, 0x00000ba, buf, 0x0000002,
			1000);
	print_bytes(buf, ret);
	printf("27 set control request returned %d\n", ret);
	usleep(890 * 1000);

	/***
	 * Read image bytes from the device
	 */
	ret = usb_bulk_read(devh, 0x00000082, imageBuf, 0x0050000, 5457);
	printf("28 bulk read returned %d, bytes: ", ret);
	usleep(100 * 1000);
	//print_bytes(imageBuf, ret);


	create_image(imageBuf, ret);

	//	ret = usb_bulk_read(devh, 0x00000082, imageBuf, 0x0050000, 5457);
	//		printf("28 bulk read returned %d, bytes: ", ret);
	//		print_bytes(imageBuf, ret);
	//	printf("\n");


	/*usleep(1 * 1000);

	 ret = usb_bulk_read(devh, 0x00000082, buf, 1024, 32457);
	 printf("29 bulk read returned %d, bytes: ", ret);
	 print_bytes(buf, ret);
	 printf("\n");
	 ret = usb_bulk_read(devh, 0x00000082, buf, 1024, 32457);
	 printf("30 bulk read returned %d, bytes: ", ret);
	 print_bytes(buf, ret);*/

	printf("\n");
	ret = usb_release_interface(devh, 0);
	assert(ret == 0);
	ret = usb_close(devh);
	assert(ret == 0);
	return 0;
}
