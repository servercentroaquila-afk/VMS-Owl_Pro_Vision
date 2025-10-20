# SDK Dahua NetSDK v3.060 - Integración VMS Áquila

## Archivos Incluidos

### Librerías Principales
- `dhnetsdk.dll` - Librería principal del SDK
- `play.dll` - Control de reproducción
- `dhconfigsdk.dll` - Configuración de dispositivos
- `avnetsdk.dll` - Audio/Video networking

### Librerías de Soporte
- `libeay32.dll` - Criptografía OpenSSL
- `ssleay32.dll` - SSL/TLS OpenSSL
- `Infra.dll` - Infraestructura base
- `RenderEngine.dll` - Motor de renderizado
- `IvsDrawer.dll` - Dibujo de overlays
- `StreamConvertor.dll` - Conversión de streams

### Archivos de Cabecera
- `dhnetsdk.h` - Definiciones principales
- `dhconfigsdk.h` - Configuración de dispositivos
- `avglobal.h` - Definiciones globales de audio/video

## Funciones Implementadas

### Autenticación
- `CLIENT_LoginWithHighLevelSecurity()` - Login seguro al dispositivo
- `CLIENT_Logout()` - Logout del dispositivo

### Búsqueda de Grabaciones
- `CLIENT_QueryRecordFile()` - Búsqueda básica de archivos
- `CLIENT_QueryRecordFileEx()` - Búsqueda extendida de archivos

### Control PTZ
- `CLIENT_PTZControl()` - Control PTZ básico

### Información del Dispositivo
- `CLIENT_QueryDeviceInfo()` - Obtener información del dispositivo

### Utilidades
- `CLIENT_Init()` - Inicializar SDK
- `CLIENT_Cleanup()` - Limpiar SDK

## Uso en VMS Áquila

El SDK se carga automáticamente en `backend/app/dahua_sdk.py`:

```python
from backend.app.dahua_sdk import DahuaSDK

# Inicializar SDK
sdk = DahuaSDK()

# Login a dispositivo
result = sdk.login("192.168.1.100", 37777, "admin", "password123")

# Obtener información del dispositivo
print(f"User ID: {result['user_id']}")
print(f"Token: {result['token']}")
```

## Configuración

El SDK se configura mediante variables de entorno:

```bash
DAHUA_SDK_PATH=./sdk/dahua/dhnetsdk.dll
```

## Notas Importantes

1. **Licencia**: Este SDK requiere licencia de Dahua
2. **Plataforma**: Compilado para Windows x64
3. **Dependencias**: Requiere Visual C++ Redistributable
4. **Threading**: No es thread-safe, usar con cuidado en aplicaciones multi-hilo
5. **Puerto por defecto**: Dahua usa puerto 37777 por defecto

## Solución de Problemas

### Error: "No se puede cargar la DLL"
- Verificar que todas las DLLs estén en el directorio
- Instalar Visual C++ Redistributable
- Verificar arquitectura (x64)

### Error de Login
- Verificar credenciales
- Verificar conectividad de red
- Verificar que el dispositivo soporte la versión del SDK
- Verificar puerto (Dahua usa 37777 por defecto)

### Error de Memoria
- Llamar `CLIENT_Cleanup()` al finalizar
- No usar el SDK en múltiples hilos simultáneamente

## Comandos PTZ Dahua

Los comandos PTZ específicos de Dahua:
- `PTZ_UP` - Mover hacia arriba
- `PTZ_DOWN` - Mover hacia abajo
- `PTZ_LEFT` - Mover hacia la izquierda
- `PTZ_RIGHT` - Mover hacia la derecha
- `PTZ_ZOOM_IN` - Zoom in
- `PTZ_ZOOM_OUT` - Zoom out
- `PTZ_STOP` - Detener movimiento
