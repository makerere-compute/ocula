/**
@author mistaguy
**/
#include "cv.h"
#include "cxcore.h"
#include "highgui.h"
#ifdef DLL_EXPORTS
#define DLL_API __declspec(dllexport)
#else
#define DLL_API __declspec(dllimport)
#endif
/**
parameters used in the project
**/
extern "C" DLL_API int SURF_EXTENDED = 0;
extern "C" DLL_API int SURF_HESSIAN_THRESHOLD = 500;
extern "C" DLL_API int SURF_NOCTAVES = 2;
extern "C" DLL_API int SURF_NOCTAVELAYERS = 2; 
extern "C" DLL_API int MATCH_THRESHOLD = 20;
extern "C" DLL_API int MATCHES = 0;
extern "C" DLL_API int FEATURES = 0;
/**
functions used for diagnosis
**/
extern "C" DLL_API int getMatchThreshold();
extern "C" DLL_API int getMatches();
extern "C" DLL_API int getFeatures();
extern "C" DLL_API void setMatchThreshold(int t);
extern "C" DLL_API void disposeDLL();
extern "C" DLL_API short detectParasite(const char * in_file);