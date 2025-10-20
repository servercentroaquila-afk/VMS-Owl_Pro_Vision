# VMS Áquila - Sistema de Gestión de Video

Sistema de gestión de video (VMS) escalable para visualización de 300+ cámaras con soporte para dispositivos Hikvision y Dahua.

## 🚀 Características

- **Soporte Multi-Marca**: Integración con SDKs oficiales de Hikvision (HCNetSDK) y Dahua (NetSDK)
- **Streaming en Tiempo Real**: Visualización de hasta 300+ cámaras simultáneas usando HLS
- **Reproducción de Grabaciones**: Consulta y reproducción de grabaciones históricas on-demand
- **Control PTZ**: Control de cámaras PTZ desde la interfaz web
- **Arquitectura Escalable**: Diseño modular con Docker y Kubernetes
- **Interfaz Moderna**: Frontend React con Tailwind CSS

## 📋 Requisitos

### Hardware Recomendado (300 cámaras)
- **CPU**: 16+ vCPU por servidor de streaming
- **RAM**: 32-64 GB por servidor
- **Red**: 1-10 Gbps
- **Almacenamiento**: SSD rápido para HLS temporal

### Software
- Docker y Docker Compose
- FFmpeg
- PostgreSQL 15+
- Node.js 18+ (para desarrollo)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd vms-aquila
```

### 2. Configuración inicial
```bash
# Crear archivo de configuración
cp .env.example .env

# Crear directorios para SDKs
make setup
```

### 3. Instalar SDKs de cámaras

#### ✅ Hikvision SDK (YA INTEGRADO)
El SDK de Hikvision v6.1.9.48 ya está integrado en el proyecto:
- **Archivos incluidos**: `HCNetSDK.dll`, `PlayCtrl.dll`, `AudioRender.dll`, `HCCore.dll`
- **Ubicación**: `backend/sdk/hikvision/`
- **Versión**: 6.1.9.48 build 20230410
- **Plataforma**: Windows x64

#### ✅ Dahua SDK (YA INTEGRADO)
El SDK de Dahua NetSDK v3.060 ya está integrado en el proyecto:
- **Archivos incluidos**: `dhnetsdk.dll`, `play.dll`, `dhconfigsdk.dll`, `avnetsdk.dll`
- **Ubicación**: `backend/sdk/dahua/`
- **Versión**: 3.060.0000001.0.R.250812
- **Plataforma**: Windows x64

### 4. Construir y ejecutar
```bash
# Construir todas las imágenes
make build

# Levantar servicios
make up

# Ver logs
make logs
```

## 🌐 Acceso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/api/docs
- **Nginx**: http://localhost

### Credenciales por defecto
- Usuario: `admin`
- Contraseña: `admin123`

## 📖 Uso

### 1. Agregar Dispositivos

Usar la API para agregar dispositivos:

```bash
curl -X POST "http://localhost:8000/api/devices" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NVR Principal",
    "brand": "hikvision",
    "ip": "192.168.1.100",
    "port": 80,
    "username": "admin",
    "password": "password123",
    "channels": 16
  }'
```

### 2. Iniciar Streams

```bash
# Iniciar stream individual
curl -X POST "http://localhost:8000/api/streams/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "channel": 1,
    "sub_stream": 0,
    "duration": 3600
  }'

# Iniciar múltiples streams
curl -X POST "http://localhost:8000/api/streams/bulk/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {"device_id": 1, "channel": 1},
    {"device_id": 1, "channel": 2},
    {"device_id": 2, "channel": 1}
  ]'
```

### 3. Consultar Grabaciones

```bash
curl "http://localhost:8000/api/recordings/1?start=2024-01-01%2000:00:00&end=2024-01-01%2023:59:59&channel=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │   Streamer      │
         │              │   (FFmpeg)      │
         │              │   Port: 1935    │
         │              └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         └──────────────►│   Nginx         │
                        │   (HLS Server)  │
                        │   Port: 80      │
                        └─────────────────┘
```

## 🔧 Comandos Útiles

```bash
# Ver estado de servicios
make status

# Ver logs en tiempo real
make logs

# Reiniciar servicios
make restart

# Acceder al shell del backend
make shell-backend

# Backup de base de datos
make backup-db

# Limpiar todo
make clean
```

## 📊 Monitoreo

### Métricas de Sistema
- **Streams activos**: `/api/streams/stats/overview`
- **Estado del sistema**: `/api/health`
- **Resumen general**: `/api/stats/overview`

### Logs
Los logs se almacenan en el directorio `./logs/` y se pueden ver con:
```bash
make logs-backend
make logs-frontend
```

## 🔒 Seguridad

### Producción
1. **Cambiar credenciales por defecto**
2. **Usar HTTPS** (configurar certificados SSL)
3. **Configurar firewall** para restringir acceso
4. **Usar Vault** para credenciales de dispositivos
5. **Implementar autenticación 2FA**

### Variables de Entorno Críticas
```bash
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://user:password@host:port/db
```

## 🚀 Despliegue en Producción

### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml vms-aquila
```

### Kubernetes
```bash
kubectl apply -f k8s-deployment.yml
```

### Escalado Horizontal
Para manejar 300+ cámaras, ejecutar múltiples instancias del streamer:

```yaml
# docker-compose.override.yml
services:
  streamer-1:
    build: ./streamer
    environment:
      - STREAMER_ID=1
  streamer-2:
    build: ./streamer
    environment:
      - STREAMER_ID=2
```

## 🐛 Solución de Problemas

### Error: SDK no encontrado
```bash
# Verificar que los SDKs estén en el lugar correcto
ls -la backend/sdk/hikvision/
ls -la backend/sdk/dahua/
```

### Error: FFmpeg no disponible
```bash
# Verificar instalación de FFmpeg
docker-compose exec backend ffmpeg -version
```

### Error: Base de datos no conecta
```bash
# Verificar estado de PostgreSQL
make shell-db
```

### Streams no se reproducen
1. Verificar conectividad RTSP
2. Revisar logs de FFmpeg
3. Verificar permisos de archivos HLS

## 📝 Licencias

- **HCNetSDK**: Licencia de Hikvision (requiere registro)
- **Dahua NetSDK**: Licencia de Dahua (requiere registro)
- **Código del proyecto**: MIT License

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📞 Soporte

Para soporte técnico o consultas:
- Crear issue en GitHub
- Documentación API: http://localhost:8000/api/docs
- Logs del sistema: `make logs`

## 🧪 Pruebas de los SDKs

### Probar Ambos SDKs
```bash
# Ejecutar script de prueba combinado
python scripts/test-both-sdks.py

# El script probará:
# - Carga de ambos SDKs
# - Inicialización
# - Conexión a dispositivos (opcional)
# - Generación de URLs RTSP
```

### Probar SDKs Individualmente
```bash
# Probar solo Hikvision
python scripts/test-hikvision-sdk.py

# Probar solo Dahua
python scripts/test-dahua-sdk.py
```

### Probar Conectividad RTSP
```bash
# Probar con cámaras de demo
bash scripts/test-rtsp.sh

# Probar con tu cámara
bash scripts/test-rtsp.sh rtsp://usuario:password@ip:puerto/stream
```

## 📄 Changelog

### v1.0.0
- ✅ **SDK Hikvision v6.1.9.48 integrado**
- ✅ **SDK Dahua NetSDK v3.060 integrado**
- Soporte completo para Hikvision y Dahua
- Interfaz web React
- Streaming HLS en tiempo real
- Reproducción de grabaciones
- Control PTZ básico
- Arquitectura Docker
- Scripts de prueba automatizados
- Wrappers Python optimizados para ambos SDKs

---

**VMS Áquila** - Sistema de Gestión de Video Profesional
