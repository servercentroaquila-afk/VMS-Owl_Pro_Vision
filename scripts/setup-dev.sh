#!/bin/bash
# VMS Áquila - Script de configuración para desarrollo

set -e

echo "🚀 Configurando VMS Áquila para desarrollo..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

print_status "Docker y Docker Compose encontrados ✓"

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    print_status "Creando archivo .env..."
    cp .env.example .env
    print_warning "Archivo .env creado. Ajusta las variables según tu configuración."
else
    print_status "Archivo .env ya existe ✓"
fi

# Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p backend/sdk/hikvision
mkdir -p backend/sdk/dahua
mkdir -p logs
mkdir -p hls

print_status "Directorios creados ✓"

# Verificar SDKs
print_warning "IMPORTANTE: Debes instalar los SDKs de Hikvision y Dahua:"
echo "  - Hikvision: Descargar HCNetSDK desde https://www.hikvision.com/en/support/download/sdk/"
echo "  - Dahua: Descargar NetSDK desde https://www.dahuasecurity.com/support/download/sdk"
echo ""
echo "Coloca los archivos en:"
echo "  - backend/sdk/hikvision/ (HCNetSDK.dll, PlayCtrl.dll, etc.)"
echo "  - backend/sdk/dahua/ (dhnetsdk.dll, dhplay.dll, etc.)"
echo ""

# Construir imágenes Docker
print_status "Construyendo imágenes Docker..."
docker-compose build

if [ $? -eq 0 ]; then
    print_status "Imágenes construidas correctamente ✓"
else
    print_error "Error construyendo imágenes Docker"
    exit 1
fi

# Iniciar servicios
print_status "Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
print_status "Esperando a que los servicios estén listos..."
sleep 10

# Verificar salud de los servicios
print_status "Verificando salud de los servicios..."

# Verificar backend
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    print_status "Backend API: ✓ Funcionando"
else
    print_warning "Backend API: ⚠ No disponible aún"
fi

# Verificar frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "Frontend: ✓ Funcionando"
else
    print_warning "Frontend: ⚠ No disponible aún"
fi

# Verificar base de datos
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    print_status "Base de datos: ✓ Funcionando"
else
    print_warning "Base de datos: ⚠ No disponible aún"
fi

echo ""
print_status "🎉 Configuración completada!"
echo ""
echo "Accede a la aplicación en:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - Documentación API: http://localhost:8000/api/docs"
echo ""
echo "Credenciales por defecto:"
echo "  - Usuario: admin"
echo "  - Contraseña: admin123"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: make logs"
echo "  - Detener servicios: make down"
echo "  - Reiniciar: make restart"
echo "  - Estado: make status"
echo ""
print_warning "Recuerda instalar los SDKs de las cámaras antes de usar el sistema."
