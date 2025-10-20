#!/bin/bash
# VMS Áquila - Script para probar conectividad RTSP

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    print_error "FFmpeg no está instalado. Instálalo primero:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: https://ffmpeg.org/download.html"
    exit 1
fi

print_status "FFmpeg encontrado ✓"

# Función para probar URL RTSP
test_rtsp() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    print_header "Probando $name: $url"
    
    if timeout $timeout ffmpeg -rtsp_transport tcp -i "$url" -t 5 -f null - 2>/dev/null; then
        print_status "$name: ✓ Conectado correctamente"
        return 0
    else
        print_error "$name: ✗ No se pudo conectar"
        return 1
    fi
}

# URLs de prueba (cámaras públicas de prueba)
print_header "Probando conectividad RTSP con cámaras de prueba..."

# Cámaras de prueba públicas (pueden no estar disponibles)
test_rtsp "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov" "Demo Stream 1" 15
test_rtsp "rtsp://freja.hiof.no:1935/rtplive/definst/hessdalen02.stream" "Demo Stream 2" 15

echo ""
print_header "Probando con URLs personalizadas..."

# Si se proporcionan argumentos, probar esas URLs
if [ $# -gt 0 ]; then
    for url in "$@"; do
        test_rtsp "$url" "URL personalizada" 15
    done
else
    echo "Para probar URLs personalizadas, ejecuta:"
    echo "  $0 rtsp://usuario:password@ip:puerto/stream"
    echo ""
    echo "Ejemplos de URLs RTSP:"
    echo "  Hikvision: rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101"
    echo "  Dahua: rtsp://admin:password@192.168.1.100/cam/realmonitor?channel=1&subtype=0"
fi

echo ""
print_status "Pruebas completadas!"
echo ""
print_warning "Nota: Si las cámaras de prueba no funcionan, es normal."
print_warning "El objetivo es verificar que FFmpeg puede conectarse a streams RTSP."
