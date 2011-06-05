#pragma once

typedef enum 
{
    COMMAND_BUILDGRAPH,
    COMMAND_RUNGRAPH,
    COMMAND_SHUTDOWN,
    COMMAND_STARTCAPTURE,
    COMMAND_STOPCAPTURE,
	COMMAND_STILLIMAGE,
    COMMAND_NOCOMMAND
} GRAPHCOMMANDS;

class CGraphManager
{
public:
    CGraphManager();
    ~CGraphManager();

    HRESULT Init();
    HRESULT BuildCaptureGraph();
    HRESULT RunCaptureGraph();
    HRESULT StartRecordVideo();
    HRESULT StopRecordVideo();
	HRESULT CaptureStillImage(WCHAR * ImageLocation);
    HRESULT ShutDown();
    HRESULT RegisterNotificationWindow( HWND hwnd );

private:

    static DWORD WINAPI ThreadProc( LPVOID lpParameter );
    HRESULT CreateCaptureGraphInternal();
    HRESULT RunCaptureGraphInternal();
    HRESULT StartCaptureVideoInternal();
    HRESULT StopCaptureVideoInternal();
	HRESULT CaptureStillImageInternal();
    HRESULT NotifyMessage( DSHOW_MESSAGE message, WCHAR *wzText );
    HRESULT ProcessCommand();
    HRESULT ProcessDShowEvent();
	HRESULT GetFirstCameraDriver( WCHAR *wzName );


    HANDLE          m_handle[2];
    HWND            m_hwnd;
    DWORD           m_dwThreadId;
    HANDLE          m_hThread;
    HANDLE          m_hCommandCompleted;
    GRAPHCOMMANDS   m_currentCommand;
    BOOL            m_fGraphBuilt;
	WCHAR *			m_StillImageLocation;

    CComPtr<ICaptureGraphBuilder2>  m_pCaptureGraphBuilder;
	CComPtr<IBaseFilter>			m_pVideoCaptureFilter;
	CComPtr<IImageSinkFilter>	    m_pImageSinkFilter;
}; 