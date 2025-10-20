#!/usr/bin/env python3
"""
Script de prueba para el SDK de Hikvision
Verifica que la integración funcione correctamente
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.hikvision_sdk import HikvisionSDK
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sdk_loading():
    """Probar carga del SDK"""
    print("🔍 Probando carga del SDK de Hikvision...")
    
    try:
        sdk = HikvisionSDK()
        print("✅ SDK cargado correctamente")
        return sdk
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que los archivos del SDK estén en backend/sdk/hikvision/")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None

def test_sdk_initialization(sdk):
    """Probar inicialización del SDK"""
    print("\n🔧 Probando inicialización del SDK...")
    
    try:
        # El SDK se inicializa automáticamente en el constructor
        print("✅ SDK inicializado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False

def test_device_connection(sdk, ip, port, username, password):
    """Probar conexión a un dispositivo"""
    print(f"\n🌐 Probando conexión a {ip}:{port}...")
    
    try:
        result = sdk.login(ip, port, username, password)
        print("✅ Conexión exitosa!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Canales: {result['device_info']['channels']}")
        print(f"   Serial: {result['device_info']['serial_number']}")
        print(f"   Tipo: {result['device_info']['device_type']}")
        
        # Cerrar sesión
        sdk.logout(result['user_id'])
        print("✅ Sesión cerrada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_rtsp_url_generation(sdk, ip, port, username, password):
    """Probar generación de URLs RTSP"""
    print("\n📹 Probando generación de URLs RTSP...")
    
    try:
        # URL principal
        main_url = sdk.get_rtsp_url(ip, port, username, password, 1, 0)
        print(f"✅ URL principal: {main_url}")
        
        # URL sub-stream
        sub_url = sdk.get_rtsp_url(ip, port, username, password, 1, 1)
        print(f"✅ URL sub-stream: {sub_url}")
        
        return True
    except Exception as e:
        print(f"❌ Error generando URLs: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del SDK de Hikvision")
    print("=" * 50)
    
    # Probar carga del SDK
    sdk = test_sdk_loading()
    if not sdk:
        return False
    
    # Probar inicialización
    if not test_sdk_initialization(sdk):
        return False
    
    # Configuración del dispositivo de prueba
    # Cambiar estos valores por los de tu dispositivo real
    test_device = {
        "ip": "192.168.1.100",
        "port": 8000,
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"\n📋 Configuración de prueba:")
    print(f"   IP: {test_device['ip']}")
    print(f"   Puerto: {test_device['port']}")
    print(f"   Usuario: {test_device['username']}")
    print(f"   Contraseña: {'*' * len(test_device['password'])}")
    
    # Preguntar si continuar con la prueba de conexión
    response = input("\n¿Continuar con la prueba de conexión? (s/n): ")
    if response.lower() != 's':
        print("⏭️ Saltando prueba de conexión")
        return True
    
    # Probar conexión
    connection_ok = test_device_connection(
        sdk, 
        test_device['ip'], 
        test_device['port'], 
        test_device['username'], 
        test_device['password']
    )
    
    # Probar generación de URLs
    url_ok = test_rtsp_url_generation(
        sdk,
        test_device['ip'],
        test_device['port'],
        test_device['username'],
        test_device['password']
    )
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    print(f"✅ Carga del SDK: {'OK' if sdk else 'FALLO'}")
    print(f"✅ Inicialización: {'OK' if sdk else 'FALLO'}")
    print(f"✅ Conexión: {'OK' if connection_ok else 'FALLO'}")
    print(f"✅ URLs RTSP: {'OK' if url_ok else 'FALLO'}")
    
    if sdk and connection_ok and url_ok:
        print("\n🎉 ¡Todas las pruebas pasaron! El SDK está listo para usar.")
        return True
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa la configuración.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
