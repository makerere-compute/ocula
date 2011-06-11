LOCAL_PATH := /home/jq/devpy/OpenCV-2.2.0/3rdparty/libjpeg

include $(CLEAR_VARS)

LOCAL_MODULE := jpeg

ifeq ($(TARGET_ARCH_ABI),armeabi-v7a)
LOCAL_ARM_NEON := true
endif

LOCAL_SRC_FILES :=   jfdctflt.c jquant1.c jchuff.c jutils.c jcphuff.c jdsample.c jdphuff.c jdcolor.c jidctint.c jcparam.c jcmainct.c jcapistd.c transupp.c jcmaster.c jcapimin.c jccoefct.c jfdctint.c jdatasrc.c jquant2.c jdmerge.c jdpostct.c jmemansi.c jccolor.c jcsample.c jcinit.c jdinput.c jdapimin.c jidctred.c jddctmgr.c jcomapi.c jdtrans.c jmemmgr.c jfdctfst.c jdapistd.c jdmaster.c jidctfst.c jcmarker.c jdmainct.c jctrans.c jdcoefct.c jerror.c jdhuff.c jdatadst.c jcdctmgr.c jcprepct.c jdmarker.c jidctflt.c

LOCAL_CFLAGS := 

LOCAL_C_INCLUDES :=  $(LOCAL_PATH)/../include $(LOCAL_PATH)

include $(BUILD_STATIC_LIBRARY)
