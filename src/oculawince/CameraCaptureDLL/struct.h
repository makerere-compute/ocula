typedef enum
{
    MESSAGE_INFO,
    MESSAGE_ERROR,
    MESSAGE_ENDRECORDING,
    MESSAGE_FILECAPTURED
} DSHOW_MESSAGE;


typedef struct
{
    DSHOW_MESSAGE   dwMessage;
    WCHAR*  wzMessage;
} Message; 