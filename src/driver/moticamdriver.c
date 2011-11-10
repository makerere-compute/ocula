/**
This Driver is based on usb_probe 

Function to read and write the MOTICAM 1000 board USB port 

**/


#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <usb.h>

struct usb_device *find_moticam(int vid, int pid);
void print_descriptor_info(struct usb_device *dev);
void delay_us(int us);
int getURB(FILE *fp, int *seq, int *ep, char *data, int n);
int usb_send(usb_dev_handle *h, int ep, void *data, int n, int time_out);
int usb_recv(usb_dev_handle *h, int ep, void *data, int n, int time_out);
int parse_data(char *str, char *data, int m);
int parse_file(FILE *fp, usb_dev_handle*h, int def_ep, int def_rs);
void print_bytes(char *data, int n);

void usage(char *pn)
{
  fprintf(stderr,"Usage: %s VID PID\n",pn);
}

int main(int argc, char **argv)
{
  struct usb_device *dev;
  usb_dev_handle *h;
  int r;
  int vid,pid;

  if(argc<1){
    usage(argv[0]);
    return -1;
  }

  //vid=strtol(argv[1],NULL,16);
  //pid=strtol(argv[2],NULL,16);

  vid=strtol("0x0634",NULL,16);
  pid=strtol("0x3111",NULL,16);


  dev=find_moticam(vid, pid);

  if(dev!=NULL){
    // Probe for endpoints
    print_descriptor_info(dev); 

    // Open dev
    h=usb_open(dev);
    printf("0x%08x\n",(long)h);
    
    if(h!=NULL){

      // Claim device interface
      r=usb_claim_interface(h, 0);
      printf("r=%d\n",r);
      if(r>=0){
	parse_file(stdin, h, 1, 0);
      }
      
      // Close
      usb_close(h);
    }
  } 
else
   {
    
   }   
}

#define BUFFER_SIZE 1024

int parse_file(FILE *fp, usb_dev_handle*h, int def_ep, int def_rs)
{
  char str[1024];
  char data[BUFFER_SIZE];
  char datar[BUFFER_SIZE];
  char *p;
  char command;
  int n,i;
  int ep=def_ep,rs=def_rs;
  FILE *fp1;
  
  while(!feof(fp)){
    p=fgets(str,1024,fp);
    if(p!=NULL){
      command=str[0];
      switch(command){
      case 'E':
	ep=strtol(str+1,NULL,16);
	break;
      case 'S':
	rs=strtol(str+1,NULL,16);
	break;
      case 'T':
	n=parse_data(str+1,data,BUFFER_SIZE);
	usb_send(h,ep,data,n,1000);
	break;
      case 'R':
	n=parse_data(str+1,data,BUFFER_SIZE);
	usb_send(h,ep,data,n,1000);
	usb_recv(h,ep,datar,rs,1000);
	break;
      case 'P':
	delay_us(strtol(str+1,NULL,10));
	break;
      case 'I':
	for(i=1; str[i]!='\0'; i++){
	  if(str[i]<' '){
	    str[i]='\0';
	    break;
	  }
	}
	fp1=fopen(str+1,"rt");
	if(fp1!=NULL){
	  printf("Include %s\n",str+1);
	  parse_file(fp1, h, ep, rs);
	  printf("End of include file %s\n",str+1);
	}
	else printf("Could not open file %s\n",str+1);
	break;
      case '#':
	printf("%s",str);
	break;
      };
    }
  }
  return 0;
}

struct usb_device *find_moticam(int vid, int pid)
{
  struct usb_bus *bus; 
  struct usb_device *devs, *dev=NULL;
  struct usb_bus *busses;
    
  usb_init();
  usb_find_busses();
  usb_find_devices();
    
  busses = usb_get_busses();
  
  for (bus = busses; bus; bus = bus->next) {
    
    for (devs = bus->devices; devs; devs = devs->next) {
      /* Check if this device is the one */
      printf("vid=0x%04X pid=0x%04X",devs->descriptor.idVendor,devs->descriptor.idProduct);
      if(devs->descriptor.idVendor==vid && devs->descriptor.idProduct==pid){
	printf(" <---");
	dev=devs;
      }
      printf("\n");
    }
  }
  return dev;
}

void print_descriptor_info(struct usb_device *dev)
{
  int c,i,a,e;
  /* Loop through all of the configurations */
  printf("Number of interfaces> %d\n",dev->descriptor.bNumConfigurations);
  for (c = 0; c < dev->descriptor.bNumConfigurations; c++) {
    printf("Number of interfaces> %d\n",dev->config[c].bNumInterfaces);
    /* Loop through all of the interfaces */
    for (i = 0; i < dev->config[c].bNumInterfaces; i++) {
      printf("Number of altsettings> %d\n",dev->config[c].interface[i].num_altsetting);
      /* Loop through all of the alternate settings */
      for (a = 0; a < dev->config[c].interface[i].num_altsetting; a++) {
	printf("Number of endpoints> %d\n",dev->config[c].interface[i].altsetting[a].bNumEndpoints);
	for(e=0; e<dev->config[c].interface[i].altsetting[a].bNumEndpoints; e++){
	  printf("EP address=%x\t",dev->config[c].interface[i].altsetting[a].endpoint[e].bEndpointAddress);
	  printf("max packet size=%d\t",dev->config[c].interface[i].altsetting[a].endpoint[e].wMaxPacketSize);
	  printf("\n");
	}
      }
    }
  }
}

int usb_send(usb_dev_handle *h, int ep, void *data, int n, int time_out)
{
  int r,i;
  r=usb_bulk_write(h, ep, data, n, time_out);
  printf("TXed %d bytes: ",r);
  print_bytes(data,r);
  printf("\n");
  return r;
} 

int usb_recv(usb_dev_handle *h, int ep, void *data, int n, int time_out)
{
  int r,i;
  r=usb_bulk_read(h, ep, data, n, time_out);
  printf("RXed %d bytes: ",r);
  print_bytes(data,r);
  printf("\n");
  return r;
} 

void print_bytes(char *data, int n)
{
  int i,c;
  for(i=0; i<n; i++){
    if(i%8==0)printf(" ");
    printf("%02x ", data[i]&0xff);
  }
  printf("\t");
  for(i=0; i<n; i++){
    c=data[i];
    if(c>=32 && c<128)printf("%c",c);
    else printf(".");
  }
}

void delay_us(int us){
  int i;
  for(i=0; i<us; i++){
    struct timespec ts={0,1000}; // 1,000 nanosecond
    nanosleep(&ts,NULL);
  }
}

int parse_data(char *str, char *data, int m)
{
  int i,j=0;
  char val;
  for(i=0; i<m; i++){
    if(str[j]=='\0')break;
    val=str[j++]-'0';
    if(val>9)val=val-7;
    if(val>9)val=val-32;
    data[i]=val<<4;
    if(str[j]=='\0')break;
    val=str[j++]-'0';
    if(val>9)val=val-7;
    if(val>15)val=val-32;
    data[i]+=val;
  }
  return i;
}
