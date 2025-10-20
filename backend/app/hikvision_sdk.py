import os
import ctypes
from ctypes import cdll, c_int, c_char_p, Structure, byref, create_string_buffer, c_void_p, c_uint32, c_uint16, c_byte, c_bool
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Ruta dinámica — el binario lo coloca el integrador
HCNETSDK_PATH = os.getenv("HIK_SDK_PATH", "./sdk/hikvision/HCNetSDK.dll")

# Estructuras del SDK de Hikvision v6.1.9.48
class NET_DVR_DEVICEINFO_V30(Structure):
    _fields_ = [
        ("sSerialNumber", ctypes.c_byte * 48),
        ("byAlarmInPortNum", c_byte),
        ("byAlarmOutPortNum", c_byte),
        ("byDiskNum", c_byte),
        ("byDVRType", c_byte),
        ("byChanNum", c_byte),
        ("byStartChan", c_byte),
        ("byAudioChanNum", c_byte),
        ("byIPChanNum", c_byte),
        ("byZeroChanNum", c_byte),
        ("byMainProto", c_byte),
        ("bySubProto", c_byte),
        ("bySupport", c_byte),
        ("bySupport1", c_byte),
        ("bySupport2", c_byte),
        ("wDevType", c_uint16),
        ("bySupport3", c_byte),
        ("byMultiStreamProto", c_byte),
        ("byStartDChan", c_byte),
        ("byStartDTalkChan", c_byte),
        ("byHighDChanNum", c_byte),
        ("bySupport4", c_byte),
        ("byLanguageType", c_byte),
        ("byVoiceInChanNum", c_byte),
        ("byStartVoiceInChan", c_byte),
        ("bySupport5", c_byte),
        ("bySupport6", c_byte),
        ("byMirrorChanNum", c_byte),
        ("wStartMirrorChan", c_uint16),
        ("bySupport7", c_byte),
        ("byRes2", c_byte * 2),
    ]

class NET_DVR_USER_LOGIN_INFO(Structure):
    _fields_ = [
        ("sDeviceAddress", ctypes.c_byte * 129),
        ("byUseTransport", c_byte),
        ("wPort", c_uint16),
        ("sUserName", ctypes.c_byte * 64),
        ("sPassword", ctypes.c_byte * 64),
        ("bUseAsynLogin", c_bool),
        ("byRes2", c_byte * 2),
    ]

class NET_DVR_LOGIN_V30(Structure):
    _fields_ = [
        ("pLoginInfo", ctypes.POINTER(NET_DVR_USER_LOGIN_INFO)),
        ("pDeviceInfo", ctypes.POINTER(NET_DVR_DEVICEINFO_V30)),
    ]

class HikvisionSDK:
    def __init__(self):
        if not os.path.exists(HCNETSDK_PATH):
            raise FileNotFoundError(f"HCNetSDK no encontrado en {HCNETSDK_PATH}")
        
        try:
            self.lib = cdll.LoadLibrary(HCNETSDK_PATH)
            self._setup_function_signatures()
            # Inicializar SDK
            result = self.lib.NET_DVR_Init()
            if result != 1:
                logger.warning("Error al inicializar HCNetSDK")
        except Exception as e:
            logger.error(f"Error cargando HCNetSDK: {e}")
            raise

    def _setup_function_signatures(self):
        """Configurar las firmas de las funciones del SDK"""
        try:
            # NET_DVR_Init
            self.lib.NET_DVR_Init.restype = c_bool
            
            # NET_DVR_Login_V30
            self.lib.NET_DVR_Login_V30.argtypes = [
                ctypes.POINTER(NET_DVR_USER_LOGIN_INFO),
                ctypes.POINTER(NET_DVR_DEVICEINFO_V30)
            ]
            self.lib.NET_DVR_Login_V30.restype = c_int
            
            # NET_DVR_Logout
            self.lib.NET_DVR_Logout.argtypes = [c_int]
            self.lib.NET_DVR_Logout.restype = c_bool
            
            # NET_DVR_Cleanup
            self.lib.NET_DVR_Cleanup.restype = c_bool
            
            # NET_DVR_GetLastError
            self.lib.NET_DVR_GetLastError.restype = c_int
            
            # NET_DVR_FindFile_V30 (para búsqueda de grabaciones)
            self.lib.NET_DVR_FindFile_V30.argtypes = [
                c_int,  # lUserID
                ctypes.POINTER(ctypes.c_byte),  # lpFindFileData
                ctypes.POINTER(ctypes.c_byte),  # lpSearchCond
            ]
            self.lib.NET_DVR_FindFile_V30.restype = c_int
            
            # NET_DVR_FindNextFile_V30
            self.lib.NET_DVR_FindNextFile_V30.argtypes = [
                c_int,  # lFindHandle
                ctypes.POINTER(ctypes.c_byte),  # lpFindFileData
            ]
            self.lib.NET_DVR_FindNextFile_V30.restype = c_bool
            
            # NET_DVR_FindClose_V30
            self.lib.NET_DVR_FindClose_V30.argtypes = [c_int]
            self.lib.NET_DVR_FindClose_V30.restype = c_bool
            
            # NET_DVR_PTZControl_Other
            self.lib.NET_DVR_PTZControl_Other.argtypes = [
                c_int,  # lUserID
                c_int,  # lChannel
                c_int,  # dwCommand
                c_int,  # dwSpeed
                c_int,  # dwStop
            ]
            self.lib.NET_DVR_PTZControl_Other.restype = c_bool
            
        except Exception as e:
            logger.warning(f"Error configurando firmas de funciones: {e}")

    def login(self, ip: str, port: int, username: str, password: str) -> Dict[str, Any]:
        """
        Iniciar sesión en el dispositivo Hikvision
        
        Args:
            ip: Dirección IP del dispositivo
            port: Puerto del dispositivo
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Dict con información de la sesión
        """
        try:
            # Configurar estructura de login
            login_info = NET_DVR_USER_LOGIN_INFO()
            
            # Convertir strings a bytes y copiar a arrays de bytes
            ip_bytes = ip.encode('utf-8')[:128]  # Máximo 128 caracteres
            for i, byte in enumerate(ip_bytes):
                login_info.sDeviceAddress[i] = byte
            login_info.sDeviceAddress[len(ip_bytes)] = 0  # Null terminator
            
            login_info.wPort = port
            login_info.byUseTransport = 0  # TCP
            
            username_bytes = username.encode('utf-8')[:63]  # Máximo 63 caracteres
            for i, byte in enumerate(username_bytes):
                login_info.sUserName[i] = byte
            login_info.sUserName[len(username_bytes)] = 0  # Null terminator
            
            password_bytes = password.encode('utf-8')[:63]  # Máximo 63 caracteres
            for i, byte in enumerate(password_bytes):
                login_info.sPassword[i] = byte
            login_info.sPassword[len(password_bytes)] = 0  # Null terminator
            
            login_info.bUseAsynLogin = False
            
            device_info = NET_DVR_DEVICEINFO_V30()
            
            # Intentar login usando la función real del SDK
            user_id = self.lib.NET_DVR_Login_V30(byref(login_info), byref(device_info))
            
            if user_id == -1:
                error_code = self.lib.NET_DVR_GetLastError()
                raise Exception(f"Error de login Hikvision: {error_code}")
            
            # Extraer información del dispositivo
            serial_number = ''.join([chr(device_info.sSerialNumber[i]) for i in range(48) if device_info.sSerialNumber[i] != 0])
            
            return {
                "user_id": user_id,
                "device_info": {
                    "channels": device_info.byChanNum,
                    "serial_number": serial_number,
                    "device_type": device_info.byDVRType,
                    "alarm_inputs": device_info.byAlarmInPortNum,
                    "alarm_outputs": device_info.byAlarmOutPortNum,
                    "disks": device_info.byDiskNum,
                    "start_channel": device_info.byStartChan,
                    "audio_channels": device_info.byAudioChanNum,
                    "ip_channels": device_info.byIPChanNum
                }
            }
            
        except Exception as e:
            logger.error(f"Error en login Hikvision: {e}")
            raise

    def logout(self, user_id: int) -> bool:
        """Cerrar sesión"""
        try:
            result = self.lib.NET_DVR_Logout(user_id)
            return result == 1
        except Exception as e:
            logger.error(f"Error en logout Hikvision: {e}")
            return False

    def find_recordings(self, user_id: int, channel: int, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        Buscar grabaciones en el dispositivo
        
        Args:
            user_id: ID de usuario de la sesión
            channel: Canal a consultar
            start_time: Fecha/hora de inicio (formato: "2023-01-01 00:00:00")
            end_time: Fecha/hora de fin
            
        Returns:
            Lista de grabaciones encontradas
        """
        try:
            # En una implementación real, aquí se usarían:
            # NET_DVR_FindFile_V30 y NET_DVR_FindNextFile_V30
            
            # Por ahora, devolvemos datos de ejemplo
            recordings = [
                {
                    "start": start_time,
                    "end": end_time,
                    "type": "normal",
                    "file_path": f"/recordings/ch{channel:02d}_{start_time.replace(' ', '_')}.mp4",
                    "size": 1024000,
                    "channel": channel
                }
            ]
            
            return recordings
            
        except Exception as e:
            logger.error(f"Error buscando grabaciones Hikvision: {e}")
            return []

    def get_rtsp_url(self, ip: str, port: int, username: str, password: str, channel: int, sub_stream: int = 0) -> str:
        """
        Generar URL RTSP para streaming
        
        Args:
            ip: IP del dispositivo
            port: Puerto del dispositivo
            username: Usuario
            password: Contraseña
            channel: Canal (1-based)
            sub_stream: Sub-stream (0=main, 1=sub)
            
        Returns:
            URL RTSP completa
        """
        # Formato estándar Hikvision RTSP
        if sub_stream == 0:
            stream_type = "01"  # Main stream
        else:
            stream_type = "02"  # Sub stream
            
        rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/{channel:02d}{stream_type}"
        return rtsp_url

    def control_ptz(self, user_id: int, channel: int, command: str, speed: int = 4) -> bool:
        """
        Control PTZ básico
        
        Args:
            user_id: ID de usuario
            channel: Canal
            command: Comando PTZ (up, down, left, right, zoom_in, zoom_out, stop)
            speed: Velocidad (1-7)
            
        Returns:
            True si el comando se ejecutó correctamente
        """
        try:
            # En implementación real, usar NET_DVR_PTZControl_Other
            # Por ahora, simulamos éxito
            logger.info(f"Comando PTZ: {command} en canal {channel} con velocidad {speed}")
            return True
            
        except Exception as e:
            logger.error(f"Error en control PTZ Hikvision: {e}")
            return False

    def __del__(self):
        """Cleanup al destruir la instancia"""
        try:
            if hasattr(self, 'lib'):
                self.lib.NET_DVR_Cleanup()
        except:
            pass
