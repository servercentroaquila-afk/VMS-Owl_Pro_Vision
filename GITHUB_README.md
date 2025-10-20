# VMS Owl Pro Vision 🦉

Sistema de Gestión de Video (VMS) profesional para visualización de 300+ cámaras con soporte nativo para dispositivos Hikvision y Dahua.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 🚀 Características Principales

- **🎥 Soporte Multi-Marca**: Integración nativa con Hikvision (HCNetSDK v6.1.9.48) y Dahua (NetSDK v3.060)
- **📺 Streaming en Tiempo Real**: Visualización de hasta 300+ cámaras simultáneas usando HLS
- **🔍 Reproducción de Grabaciones**: Consulta y reproducción de grabaciones históricas on-demand
- **🎮 Control PTZ**: Control completo de cámaras PTZ desde la interfaz web
- **🏗️ Arquitectura Escalable**: Diseño modular con Docker y Kubernetes
- **💻 Interfaz Moderna**: Frontend React con Tailwind CSS y componentes optimizados
- **🔒 Seguridad**: Autenticación JWT y validación de datos robusta

## 📋 Requisitos del Sistema

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

## 🛠️ Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/servercentroaquila-afk/VMS-Owl_Pro_Vision.git
cd VMS-Owl_Pro_Vision
```

### 2. Configuración Inicial
```bash
# Crear archivo de configuración
cp .env.example .env

# Configurar SDKs (ver sección SDKs)
make setup
```

### 3. Instalar SDKs de Cámaras

#### ✅ Hikvision SDK (YA INTEGRADO)
El SDK de Hikvision v6.1.9.48 ya está integrado:
- **Archivos**: `HCNetSDK.dll`, `PlayCtrl.dll`, `AudioRender.dll`, `HCCore.dll`
- **Ubicación**: `backend/sdk/hikvision/`

#### ✅ Dahua SDK (YA INTEGRADO)
El SDK de Dahua NetSDK v3.060 ya está integrado:
- **Archivos**: `dhnetsdk.dll`, `play.dll`, `dhconfigsdk.dll`, `avnetsdk.dll`
- **Ubicación**: `backend/sdk/dahua/`

### 4. Construir y Ejecutar
```bash
# Construir todas las imágenes
make build

# Levantar servicios
make up

# Ver logs
make logs
```

## 🌐 Acceso al Sistema

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/api/docs
- **Nginx**: http://localhost

### Credenciales por Defecto
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 🧪 Pruebas del Sistema

### Probar Ambos SDKs
```bash
# Ejecutar script de prueba combinado
python scripts/test-both-sdks.py
```

### Probar SDKs Individualmente
```bash
# Solo Hikvision
python scripts/test-hikvision-sdk.py

# Solo Dahua
python scripts/test-dahua-sdk.py
```

### Probar Conectividad RTSP
```bash
# Probar con cámaras de demo
bash scripts/test-rtsp.sh

# Probar con tu cámara
bash scripts/test-rtsp.sh rtsp://usuario:password@ip:puerto/stream
```

## 📖 Uso del Sistema

### Agregar Dispositivos

Usar la API para agregar dispositivos:

```bash
curl -X POST "http://localhost:8000/api/devices" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "NVR Principal",
    "brand": "hikvision",
    "ip": "192.168.1.100",
    "port": 8000,
    "username": "admin",
    "password": "password123",
    "channels": 16
  }'
```

### Iniciar Streams

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
```

## 🏗️ Arquitectura del Sistema

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
# Gestión básica
make up          # Levantar servicios
make down        # Detener servicios
make logs        # Ver logs
make status      # Estado de servicios

# Desarrollo
make dev         # Modo desarrollo
make shell-backend  # Acceder al backend
make test        # Ejecutar tests

# Mantenimiento
make backup-db   # Backup de BD
make clean       # Limpiar todo
```

## 🔒 Seguridad

### Producción
1. **Cambiar credenciales por defecto**
2. **Usar HTTPS** (configurar certificados SSL)
3. **Configurar firewall** para restringir acceso
4. **Usar Vault** para credenciales de dispositivos
5. **Implementar autenticación 2FA**

## 🚀 Despliegue en Producción

### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml vms-owl-pro
```

### Kubernetes
```bash
kubectl apply -f k8s-deployment.yml
```

## 📊 Monitoreo

### Métricas de Sistema
- **Streams activos**: `/api/streams/stats/overview`
- **Estado del sistema**: `/api/health`
- **Resumen general**: `/api/stats/overview`

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Crear issue en GitHub
- Documentación API: http://localhost:8000/api/docs
- Logs del sistema: `make logs`

## 📄 Changelog

### v1.0.0
- ✅ **SDK Hikvision v6.1.9.48 integrado**
- ✅ **SDK Dahua NetSDK v3.060 integrado**
- Soporte completo para Hikvision y Dahua
- Interfaz web React moderna
- Streaming HLS en tiempo real
- Reproducción de grabaciones
- Control PTZ básico
- Arquitectura Docker escalable
- Scripts de prueba automatizados
- Wrappers Python optimizados para ambos SDKs

---

**VMS Owl Pro Vision** - Sistema de Gestión de Video Profesional

Desarrollado por [Server Centro Áquila](https://github.com/servercentroaquila-afk)
