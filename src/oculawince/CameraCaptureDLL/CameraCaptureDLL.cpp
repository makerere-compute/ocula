// CameraCaptureDLL.cpp : Defines the entry point for the DLL application to Manage code ie C#.
//

#include "stdafx.h"
#include <windows.h>
#include <winbase.h>
#include <objbase.h>
#include <commctrl.h>

CGraphManager *m_pGraphManager;

BOOL APIENTRY DllMain( HANDLE hModule, 
                       DWORD  ul_reason_for_call, 
                       LPVOID lpReserved
					 )
{

	if (ul_reason_for_call==DLL_PROCESS_ATTACH)
		CoInitializeEx(NULL, COINIT_MULTITHREADED);
	if (ul_reason_for_call==DLL_PROCESS_DETACH)
		CoUninitialize();
    return TRUE;
}

extern "C" bool __declspec(dllexport) InitializeGraph(HWND hWnd)
{
	HRESULT hr = S_OK;

    // Create the graph manager. This will control the dshow capture pipeline
    m_pGraphManager = new CGraphManager();
    if( m_pGraphManager == NULL )
    {
        ERR( E_OUTOFMEMORY );
    }

    CHK( m_pGraphManager->RegisterNotificationWindow( hWnd ));

    CHK( m_pGraphManager->Init());
    CHK( m_pGraphManager->BuildCaptureGraph());

    CHK( m_pGraphManager->RunCaptureGraph());

Cleanup:
    return hr==S_OK; 
}

extern "C" bool __declspec(dllexport) CaptureStill(WCHAR* LocationToStore)
{
	m_pGraphManager->CaptureStillImage(LocationToStore);
	return true;
}
