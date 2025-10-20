# Configuración del SDK de Hikvision v6.1.9.48

# Versión del SDK
SDK_VERSION = "6.1.9.48"
SDK_BUILD = "20230410"
SDK_PLATFORM = "win64"

# Archivos principales
MAIN_DLL = "HCNetSDK.dll"
PLAY_DLL = "PlayCtrl.dll"
AUDIO_DLL = "AudioRender.dll"
CORE_DLL = "HCCore.dll"

# Archivos de soporte
SUPPORT_DLLS = [
    "libcrypto-1_1-x64.dll",
    "libssl-1_1-x64.dll", 
    "zlib1.dll",
    "OpenAL32.dll"
]

# Headers
HEADERS = [
    "HCNetSDK.h",
    "DataType.h"
]

# Configuración de funciones
FUNCTIONS = {
    "NET_DVR_Init": {"return": "bool"},
    "NET_DVR_Login_V30": {"return": "int", "args": ["login_info", "device_info"]},
    "NET_DVR_Logout": {"return": "bool", "args": ["user_id"]},
    "NET_DVR_Cleanup": {"return": "bool"},
    "NET_DVR_GetLastError": {"return": "int"},
    "NET_DVR_FindFile_V30": {"return": "int", "args": ["user_id", "find_data", "search_cond"]},
    "NET_DVR_FindNextFile_V30": {"return": "bool", "args": ["find_handle", "find_data"]},
    "NET_DVR_FindClose_V30": {"return": "bool", "args": ["find_handle"]},
    "NET_DVR_PTZControl_Other": {"return": "bool", "args": ["user_id", "channel", "command", "speed", "stop"]}
}
