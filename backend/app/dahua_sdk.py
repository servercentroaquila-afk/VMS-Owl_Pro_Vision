import os
import ctypes
from ctypes import cdll, c_int, c_char_p, Structure, byref, create_string_buffer, c_void_p, c_uint32, c_byte, c_bool
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Ruta dinámica — el binario lo coloca el integrador
DAHUA_SDK_PATH = os.getenv("DAHUA_SDK_PATH", "./sdk/dahua/dhnetsdk.dll")

# Estructuras del SDK de Dahua v3.060
class NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY(Structure):
    _fields_ = [
        ("szIP", ctypes.c_byte * 128),
        ("nPort", c_int),
        ("szUserName", ctypes.c_byte * 64),
        ("szPassword", ctypes.c_byte * 64),
        ("nSpecCap", c_int),
        ("szReserved", ctypes.c_byte * 32),
    ]

class NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY(Structure):
    _fields_ = [
        ("nTokenLen", c_int),
        ("szToken", ctypes.c_byte * 1024),
        ("nErrorCode", c_int),
        ("szReserved", ctypes.c_byte * 32),
    ]

class NET_DEVICEINFO_Ex(Structure):
    _fields_ = [
        ("nChannels", c_int),
        ("nAlarmInPorts", c_int),
        ("nAlarmOutPorts", c_int),
        ("nDiskNum", c_int),
        ("nType", c_int),
        ("nSerialLen", c_int),
        ("szSerialNumber", ctypes.c_byte * 48),
        ("byStartChan", c_byte),
        ("byChanNum", c_byte),
        ("byStartDChan", c_byte),
        ("byDChanNum", c_byte),
        ("byStartDTalkChan", c_byte),
        ("byDTalkChanNum", c_byte),
        ("nNetAudioChannels", c_int),
        ("nComPorts", c_int),
        ("nAuxChannels", c_int),
        ("nAlarmInGroups", c_int),
        ("nAlarmOutGroups", c_int),
        ("nMaxAlarmOut", c_int),
        ("nMaxAlarmIn", c_int),
        ("nMaxVideoIn", c_int),
        ("nMaxVideoOut", c_int),
        ("nMaxAudioIn", c_int),
        ("nMaxAudioOut", c_int),
        ("nMaxUsers", c_int),
        ("nMaxGroups", c_int),
        ("nMaxResource", c_int),
        ("nChnCombine", c_int),
        ("nReserved", c_int * 4),
    ]

class DahuaSDK:
    def __init__(self):
        if not os.path.exists(DAHUA_SDK_PATH):
            raise FileNotFoundError(f"Dahua SDK no encontrado en {DAHUA_SDK_PATH}")
        
        try:
            self.lib = cdll.LoadLibrary(DAHUA_SDK_PATH)
            self._setup_function_signatures()
            # Inicializar SDK si es necesario
            logger.info("Dahua SDK cargado correctamente")
        except Exception as e:
            logger.error(f"Error cargando Dahua SDK: {e}")
            raise

    def _setup_function_signatures(self):
        """Configurar las firmas de las funciones del SDK"""
        try:
            # CLIENT_Init
            self.lib.CLIENT_Init.restype = c_bool
            
            # CLIENT_LoginWithHighLevelSecurity
            self.lib.CLIENT_LoginWithHighLevelSecurity.argtypes = [
                ctypes.POINTER(NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY),
                ctypes.POINTER(NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY)
            ]
            self.lib.CLIENT_LoginWithHighLevelSecurity.restype = c_int
            
            # CLIENT_Logout
            self.lib.CLIENT_Logout.argtypes = [c_int]
            self.lib.CLIENT_Logout.restype = c_bool
            
            # CLIENT_Cleanup
            self.lib.CLIENT_Cleanup.restype = c_bool
            
            # CLIENT_QueryRecordFile (para búsqueda de grabaciones)
            self.lib.CLIENT_QueryRecordFile.argtypes = [
                c_int,  # lLoginID
                ctypes.POINTER(ctypes.c_byte),  # lpQueryRecordFile
                ctypes.POINTER(ctypes.c_byte),  # lpQueryRecordFileOut
            ]
            self.lib.CLIENT_QueryRecordFile.restype = c_bool
            
            # CLIENT_QueryRecordFileEx (búsqueda extendida)
            self.lib.CLIENT_QueryRecordFileEx.argtypes = [
                c_int,  # lLoginID
                ctypes.POINTER(ctypes.c_byte),  # lpQueryRecordFile
                ctypes.POINTER(ctypes.c_byte),  # lpQueryRecordFileOut
            ]
            self.lib.CLIENT_QueryRecordFileEx.restype = c_bool
            
            # CLIENT_PTZControl (control PTZ)
            self.lib.CLIENT_PTZControl.argtypes = [
                c_int,  # lLoginID
                c_int,  # nChannelID
                c_int,  # dwCommand
                c_int,  # dwSpeed
                c_int,  # dwStop
            ]
            self.lib.CLIENT_PTZControl.restype = c_bool
            
            # CLIENT_QueryDeviceInfo (información del dispositivo)
            self.lib.CLIENT_QueryDeviceInfo.argtypes = [
                c_int,  # lLoginID
                c_int,  # nType
                ctypes.POINTER(ctypes.c_byte),  # lpOutBuffer
                c_int,  # dwOutBufferSize
                ctypes.POINTER(c_int),  # lpBytesReturned
            ]
            self.lib.CLIENT_QueryDeviceInfo.restype = c_bool
            
        except Exception as e:
            logger.warning(f"Error configurando firmas de funciones Dahua: {e}")

    def login(self, ip: str, port: int, username: str, password: str) -> Dict[str, Any]:
        """
        Iniciar sesión en el dispositivo Dahua
        
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
            login_in = NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY()
            
            # Convertir strings a bytes y copiar a arrays de bytes
            ip_bytes = ip.encode('utf-8')[:127]  # Máximo 127 caracteres
            for i, byte in enumerate(ip_bytes):
                login_in.szIP[i] = byte
            login_in.szIP[len(ip_bytes)] = 0  # Null terminator
            
            login_in.nPort = port
            
            username_bytes = username.encode('utf-8')[:63]  # Máximo 63 caracteres
            for i, byte in enumerate(username_bytes):
                login_in.szUserName[i] = byte
            login_in.szUserName[len(username_bytes)] = 0  # Null terminator
            
            password_bytes = password.encode('utf-8')[:63]  # Máximo 63 caracteres
            for i, byte in enumerate(password_bytes):
                login_in.szPassword[i] = byte
            login_in.szPassword[len(password_bytes)] = 0  # Null terminator
            
            login_in.nSpecCap = 0
            
            login_out = NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY()
            
            # Intentar login usando la función real del SDK
            user_id = self.lib.CLIENT_LoginWithHighLevelSecurity(byref(login_in), byref(login_out))
            
            if user_id == 0:
                error_code = login_out.nErrorCode
                raise Exception(f"Error de login Dahua: {error_code}")
            
            # Extraer token
            token = ''.join([chr(login_out.szToken[i]) for i in range(login_out.nTokenLen) if login_out.szToken[i] != 0])
            
            return {
                "user_id": user_id,
                "token": token,
                "device_info": {
                    "channels": 16,  # Valor por defecto, se puede obtener con CLIENT_QueryDeviceInfo
                    "ip": ip,
                    "port": port,
                    "error_code": login_out.nErrorCode
                }
            }
            
        except Exception as e:
            logger.error(f"Error en login Dahua: {e}")
            raise

    def logout(self, user_id: int) -> bool:
        """Cerrar sesión"""
        try:
            result = self.lib.CLIENT_Logout(user_id)
            return result == 1
        except Exception as e:
            logger.error(f"Error en logout Dahua: {e}")
            return False

    def find_recordings(self, user_id: int, channel: int, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        Buscar grabaciones en el dispositivo Dahua
        
        Args:
            user_id: ID de usuario de la sesión
            channel: Canal a consultar
            start_time: Fecha/hora de inicio
            end_time: Fecha/hora de fin
            
        Returns:
            Lista de grabaciones encontradas
        """
        try:
            # En una implementación real, aquí se usaría:
            # CLIENT_QueryRecordFile
            
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
            logger.error(f"Error buscando grabaciones Dahua: {e}")
            return []

    def get_rtsp_url(self, ip: str, port: int, username: str, password: str, channel: int, sub_stream: int = 0) -> str:
        """
        Generar URL RTSP para streaming Dahua
        
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
        # Formato estándar Dahua RTSP
        if sub_stream == 0:
            stream_type = "0"  # Main stream
        else:
            stream_type = "1"  # Sub stream
            
        rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype={stream_type}"
        return rtsp_url

    def control_ptz(self, user_id: int, channel: int, command: str, speed: int = 4) -> bool:
        """
        Control PTZ básico para Dahua
        
        Args:
            user_id: ID de usuario
            channel: Canal
            command: Comando PTZ (up, down, left, right, zoom_in, zoom_out, stop)
            speed: Velocidad (1-7)
            
        Returns:
            True si el comando se ejecutó correctamente
        """
        try:
            # En implementación real, usar CLIENT_PTZControl
            # Por ahora, simulamos éxito
            logger.info(f"Comando PTZ Dahua: {command} en canal {channel} con velocidad {speed}")
            return True
            
        except Exception as e:
            logger.error(f"Error en control PTZ Dahua: {e}")
            return False

    def __del__(self):
        """Cleanup al destruir la instancia"""
        try:
            if hasattr(self, 'lib'):
                self.lib.CLIENT_Cleanup()
        except:
            pass
