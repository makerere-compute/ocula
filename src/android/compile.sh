PKG_CONFIG_PATH=/usr/lib/pkgconfig/:${PKG_CONFIG_PATH}
export PKG_CONFIG_PATH

LD_LIBRARY_PATH=~/devpy/OpenCV-2.2.0/release/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH

#gcc `pkg-config --cflags opencv` `pkg-config --libs opencv` -o surfdetect test.cpp
gcc -I/home/jq/devpy/OpenCV-2.2.0/include/opencv -L/home/jq/devpy/OpenCV-2.2.0/release/lib -lcv -lhighgui -lstdc++ -o surfdetect test.cpp

