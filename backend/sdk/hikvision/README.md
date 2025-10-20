# SDK Hikvision v6.1.9.48 - Integración VMS Áquila

## Archivos Incluidos

### Librerías Principales
- `HCNetSDK.dll` - Librería principal del SDK
- `PlayCtrl.dll` - Control de reproducción
- `AudioRender.dll` - Renderizado de audio
- `HCCore.dll` - Funciones core del SDK

### Librerías de Soporte
- `libcrypto-1_1-x64.dll` - Criptografía OpenSSL
- `libssl-1_1-x64.dll` - SSL/TLS OpenSSL
- `zlib1.dll` - Compresión
- `OpenAL32.dll` - Audio 3D

### Archivos de Cabecera
- `HCNetSDK.h` - Definiciones principales
- `DataType.h` - Tipos de datos

## Funciones Implementadas

### Autenticación
- `NET_DVR_Login_V30()` - Login al dispositivo
- `NET_DVR_Logout()` - Logout del dispositivo

### Búsqueda de Grabaciones
- `NET_DVR_FindFile_V30()` - Iniciar búsqueda
- `NET_DVR_FindNextFile_V30()` - Obtener siguiente archivo
- `NET_DVR_FindClose_V30()` - Cerrar búsqueda

### Control PTZ
- `NET_DVR_PTZControl_Other()` - Control PTZ básico

### Utilidades
- `NET_DVR_GetLastError()` - Obtener último error
- `NET_DVR_Init()` - Inicializar SDK
- `NET_DVR_Cleanup()` - Limpiar SDK

## Uso en VMS Áquila

El SDK se carga automáticamente en `backend/app/hikvision_sdk.py`:

```python
from backend.app.hikvision_sdk import HikvisionSDK

# Inicializar SDK
sdk = HikvisionSDK()

# Login a dispositivo
result = sdk.login("192.168.1.100", 8000, "admin", "password123")

# Obtener información del dispositivo
print(f"Canales: {result['device_info']['channels']}")
print(f"Serial: {result['device_info']['serial_number']}")
```

## Configuración

El SDK se configura mediante variables de entorno:

```bash
HIK_SDK_PATH=./sdk/hikvision/HCNetSDK.dll
```

## Notas Importantes

1. **Licencia**: Este SDK requiere licencia de Hikvision
2. **Plataforma**: Compilado para Windows x64
3. **Dependencias**: Requiere Visual C++ Redistributable
4. **Threading**: No es thread-safe, usar con cuidado en aplicaciones multi-hilo

## Solución de Problemas

### Error: "No se puede cargar la DLL"
- Verificar que todas las DLLs estén en el directorio
- Instalar Visual C++ Redistributable
- Verificar arquitectura (x64)

### Error de Login
- Verificar credenciales
- Verificar conectividad de red
- Verificar que el dispositivo soporte la versión del SDK

### Error de Memoria
- Llamar `NET_DVR_Cleanup()` al finalizar
- No usar el SDK en múltiples hilos simultáneamente
