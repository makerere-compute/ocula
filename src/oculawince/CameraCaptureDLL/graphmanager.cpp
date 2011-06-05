//
// Copyright (c) Microsoft Corporation.  All rights reserved.
//
//
// Use of this source code is subject to the terms of the Microsoft end-user
// license agreement (EULA) under which you licensed this SOFTWARE PRODUCT.
// If you did not accept the terms of the EULA, you are not authorized to use
// this source code. For a copy of the EULA, please see the LICENSE.RTF on your
// install media.
//
#include "stdafx.h"

CGraphManager::CGraphManager()
: m_StillImageLocation(0)
{
	m_fGraphBuilt = FALSE;
	ZeroMemory( m_handle, sizeof( m_handle ));
	m_hwnd = 0;
	m_dwThreadId = 0;
	m_hThread = NULL;
	m_hCommandCompleted = NULL;
	m_currentCommand = COMMAND_NOCOMMAND;
}


CGraphManager::~CGraphManager()
{
    if( m_handle[0] )
    {
        CloseHandle( m_handle[0] );
    }

    if( m_handle[1] )
    {
        CloseHandle( m_handle[1] );
    }

	if (m_StillImageLocation)
	{
		delete [] m_StillImageLocation;
		m_StillImageLocation = 0;
	}
}


HRESULT
CGraphManager::Init()
{
    HRESULT hr = S_OK;

    // Create the event that will signal the thread for commands
    m_handle[0] = CreateEvent( NULL, FALSE, FALSE, NULL );
    if( m_handle[0] == NULL )
    {
        ERR( HRESULT_FROM_WIN32( GetLastError() ));
    }
    m_handle[1] = 0;

    // Create the event to sync on to wait for the command to be executed
    m_hCommandCompleted = CreateEvent( NULL, FALSE, FALSE, NULL );
    if( m_hCommandCompleted == NULL )
    {
        ERR( HRESULT_FROM_WIN32( GetLastError() ));
    }

    // CCreate the thread that will run the filtergraph. 
    // The filtergraph is runing on a background thread to prevent any window message
    // reentrancy issue. 
    m_hThread = CreateThread( NULL, 0, CGraphManager::ThreadProc, this, 0, &m_dwThreadId );
    if( m_hThread == NULL )
    {
        ERR( HRESULT_FROM_WIN32( GetLastError() ));
    }


Cleanup:
    return hr;
}


HRESULT
CGraphManager::BuildCaptureGraph()
{
    // The Graph is built on a separate thread to 
    // prevent reentrancy issues. 
    m_currentCommand = COMMAND_BUILDGRAPH;
    SetEvent( m_handle[0] );
    WaitForSingleObject( m_hCommandCompleted, INFINITE );

    return S_OK;
}


HRESULT
CGraphManager::RunCaptureGraph()
{
    // Unlike the other operations, running the graph
    // has to happen from the UI thread. 
    return RunCaptureGraphInternal();
}


HRESULT 
CGraphManager::CaptureStillImage(WCHAR * ImageLocation)
{
	if (m_StillImageLocation)
	{
		delete [] m_StillImageLocation;
	}

	m_StillImageLocation = new WCHAR [wcslen(ImageLocation)+1];
	wcscpy(m_StillImageLocation,ImageLocation);
    m_currentCommand = COMMAND_STILLIMAGE;
    SetEvent( m_handle[0] );
    WaitForSingleObject( m_hCommandCompleted, INFINITE );

    return S_OK;
}


HRESULT
CGraphManager::ShutDown()
{
    m_currentCommand = COMMAND_SHUTDOWN;
    SetEvent( m_handle[0] );
    WaitForSingleObject( m_hThread, INFINITE );

    return S_OK;
}


HRESULT
CGraphManager::RegisterNotificationWindow( HWND hwnd )
{
    m_hwnd = hwnd;
    return S_OK;
}


DWORD WINAPI 
CGraphManager::ThreadProc( LPVOID lpParameter )
{
    HRESULT       hr = S_OK;
    DWORD         dwReturnValue;
    CGraphManager *pThis = (CGraphManager*) lpParameter;
    GRAPHCOMMANDS command = COMMAND_NOCOMMAND;

    if( pThis == NULL )
    {
        return 0;
    }

    while(( command != COMMAND_SHUTDOWN ) && ( hr != S_FALSE ))
    {
		if (!pThis->m_handle[1])
			Sleep(500);
        dwReturnValue = WaitForMultipleObjects( 2, pThis->m_handle, FALSE, INFINITE );
        switch( dwReturnValue )
        {
            case WAIT_OBJECT_0:
                command = pThis->m_currentCommand;
                pThis->ProcessCommand();
                break;

            case WAIT_OBJECT_0 + 1:
                pThis->ProcessDShowEvent();
                break;

            default:
                break;
        }
    };

    return 0;
}


HRESULT
CGraphManager::ProcessCommand()
{
    HRESULT hr = S_OK;
    
    switch( m_currentCommand )
    {
        case COMMAND_BUILDGRAPH:
            hr = CreateCaptureGraphInternal();
            SetEvent( m_hCommandCompleted );
            break;

        case COMMAND_RUNGRAPH:
            hr = RunCaptureGraphInternal();
            SetEvent( m_hCommandCompleted );
            break;

		case COMMAND_STILLIMAGE:
			hr = CaptureStillImageInternal();
            SetEvent( m_hCommandCompleted );
            break;

        case COMMAND_SHUTDOWN:
            hr = S_FALSE;
            break;

        default:
            break;
    }

    return hr;
}


HRESULT
CGraphManager::ProcessDShowEvent()
{
    HRESULT hr = S_OK;
    long    lEventCode, lParam1, lParam2;

    CComPtr<IMediaEvent> pMediaEvent;
    CComPtr<IGraphBuilder> pFilterGraph;
    CComPtr<IMediaControl> pMediaControl;
    
 

    if( m_pCaptureGraphBuilder == NULL )
    {
        ERR( E_FAIL );
    }

    CHK( m_pCaptureGraphBuilder->GetFiltergraph( &pFilterGraph ));
    CHK( pFilterGraph->QueryInterface( &pMediaEvent ));
    CHK( pMediaEvent->GetEvent( &lEventCode, &lParam1, &lParam2, 0 ));

   if( lEventCode == EC_CAP_FILE_COMPLETED )
    {
        NotifyMessage( MESSAGE_FILECAPTURED, L"File captured ..." );
    }


    CHK( pMediaEvent->FreeEventParams( lEventCode, lParam1, lParam2 ));

Cleanup:
    return S_OK;
}


HRESULT 
CGraphManager::GetFirstCameraDriver( WCHAR *pwzName )
{
	HRESULT hr = S_OK;
	HANDLE	handle = NULL;
	DEVMGR_DEVICE_INFORMATION di;
	GUID guidCamera = { 0xCB998A05, 0x122C, 0x4166, 0x84, 0x6A, 0x93, 0x3E, 0x4D, 0x7E, 0x3C, 0x86 };
	// Note about the above: The driver material doesn't ship as part of the SDK. This GUID is hardcoded
	// here to be able to enumerate the camera drivers and pass the name of the driver to the video capture filter

	if( pwzName == NULL )
	{
		return E_POINTER;
	}

	di.dwSize = sizeof(di);

	handle = FindFirstDevice( DeviceSearchByGuid, &guidCamera, &di );
	if(( handle == NULL ) || ( di.hDevice == NULL ))
	{
		ERR( HRESULT_FROM_WIN32( GetLastError() ));
	}

	StringCchCopy( pwzName, MAX_PATH, di.szLegacyName );

Cleanup:
	FindClose( handle );
	return hr;
}



HRESULT
CGraphManager::CreateCaptureGraphInternal()
{
    HRESULT       hr = S_OK;
    CComVariant   varCamName;
    CPropertyBag  PropBag;
    OAEVENT       oaEvent;
	WCHAR	      wzDeviceName[ MAX_PATH + 1 ];

    CComPtr<IMediaEvent>            pMediaEvent;
    CComPtr<IGraphBuilder>          pFilterGraph;
    CComPtr<IPersistPropertyBag>    pPropertyBag;
    CComPtr<IDMOWrapperFilter>      pWrapperFilter;
    CComPtr<IBaseFilter>			pImageSinkFilter;


    //
    // Create the capture graph builder and register the filtergraph manager. 
    //
    CHK( m_pCaptureGraphBuilder.CoCreateInstance( CLSID_CaptureGraphBuilder ));
    CHK( pFilterGraph.CoCreateInstance( CLSID_FilterGraph ));
	
    CHK( m_pCaptureGraphBuilder->SetFiltergraph( pFilterGraph ));


    //
    // Create and initialize the video capture filter
    //
    CHK( m_pVideoCaptureFilter.CoCreateInstance( CLSID_VideoCapture ));
    CHK( m_pVideoCaptureFilter.QueryInterface( &pPropertyBag ));

    // We are loading the driver CAM1 in the video capture filter. 
	CHK( GetFirstCameraDriver( wzDeviceName ));
    varCamName = wzDeviceName;
    if( varCamName.vt != VT_BSTR )
    {
        ERR( E_OUTOFMEMORY );
    }

    CHK( PropBag.Write( L"VCapName", &varCamName ));   
    CHK( pPropertyBag->Load( &PropBag, NULL ));

    // Everything succeeded, the video capture filter is added to the filtergraph
    CHK( pFilterGraph->AddFilter( m_pVideoCaptureFilter, L"Video Capture Filter Source" ));

	//
	// Create the still image filter, and connect it to the video capture filter
	//
	CHK( pImageSinkFilter.CoCreateInstance( CLSID_IMGSinkFilter ));
    CHK( pFilterGraph->AddFilter( pImageSinkFilter, L"Still image filter" ));
	CHK( m_pCaptureGraphBuilder->RenderStream( &PIN_CATEGORY_STILL, &MEDIATYPE_Video, m_pVideoCaptureFilter, NULL, pImageSinkFilter ));
	CHK( pImageSinkFilter.QueryInterface( &m_pImageSinkFilter ));

    //
    // Prevent the data from flowing into the capture stream
    //
 //   CHK( m_pCaptureGraphBuilder->ControlStream( &PIN_CATEGORY_CAPTURE, &MEDIATYPE_Video, m_pVideoCaptureFilter, 0, 0 ,0,0 ));

    //
    // Let's get the handle for DShow events. The main loop will listen to both notifications from 
    // the UI thread and for DShow notifications
    //
    CHK( pFilterGraph->QueryInterface( IID_IMediaEvent, (void**) &pMediaEvent ));
    CHK( pMediaEvent->GetEventHandle( &oaEvent ));
    m_handle[1] = (HANDLE) oaEvent;

    m_fGraphBuilt = TRUE;
	NotifyMessage( MESSAGE_INFO, L"Builing the graph completed" );

Cleanup:
	if( FAILED( hr ))
	{
		NotifyMessage( MESSAGE_ERROR, L"Builing the graph failed" );
	}
    return hr;
}


HRESULT
CGraphManager::RunCaptureGraphInternal()
{
    HRESULT hr = S_OK;

    CComPtr<IGraphBuilder> pGraphBuilder;
    CComPtr<IMediaControl> pMediaControl;

    // Let's make sure that the graph has been initialized
    if(( m_pCaptureGraphBuilder == NULL ) || ( m_fGraphBuilt == FALSE ))
    {
        ERR( E_FAIL );
    }

    // Retrieve the filtergraph off the capture graph builder
    CHK( m_pCaptureGraphBuilder->GetFiltergraph( &pGraphBuilder ));

    // Get the media control interface, and run the graph
    CHK( pGraphBuilder->QueryInterface( &pMediaControl ));
    CHK( pMediaControl->Run());

    CHK( NotifyMessage( MESSAGE_INFO, L"The Graph is running" ));

Cleanup:
	if( FAILED( hr ))
	{
		NotifyMessage( MESSAGE_ERROR, L"Runing the capture graph failed" );
	}
    return hr;
}

HRESULT
CGraphManager::CaptureStillImageInternal()
{
	HRESULT hr = S_OK;
 
	CComPtr<IFileSinkFilter> pFileSink;
	CComPtr<IUnknown>		 pUnkCaptureFilter;
	CComPtr<IPin>			 pStillPin;
	CComPtr<IAMVideoControl> pVideoControl;


    if(( m_pCaptureGraphBuilder == NULL ) || ( m_fGraphBuilt == FALSE ))
    {
        ERR( E_FAIL );
    }
	

	CHK( m_pImageSinkFilter.QueryInterface( &pFileSink ));
	CHK( pFileSink->SetFileName( m_StillImageLocation, NULL ));

	CHK( m_pVideoCaptureFilter.QueryInterface( &pUnkCaptureFilter ));
	CHK( m_pCaptureGraphBuilder->FindPin( pUnkCaptureFilter, PINDIR_OUTPUT, &PIN_CATEGORY_STILL, &MEDIATYPE_Video, FALSE, 0, &pStillPin ));
	CHK( m_pVideoCaptureFilter.QueryInterface( &pVideoControl ));
	CHK( pVideoControl->SetMode( pStillPin, VideoControlFlag_Trigger ));

Cleanup:
	if( FAILED( hr ))
	{
		NotifyMessage( MESSAGE_ERROR, L"Capturing a still image failed" );
	}
    return hr;
}


HRESULT
CGraphManager::NotifyMessage( DSHOW_MESSAGE message, WCHAR *wzText )
{
    HRESULT hr = S_OK;

    if(( wzText == NULL ) || ( *wzText == NULL ))
    {
        ERR( E_POINTER );
    }

    if( m_hwnd == NULL )
    {
        return S_FALSE;
    }

    PostMessage( m_hwnd, WM_USER, 0, (LPARAM) message );

Cleanup:
    return hr;
}
