#!/usr/bin/env python3
"""
Script de prueba combinado para ambos SDKs (Hikvision y Dahua)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.hikvision_sdk import HikvisionSDK
from app.dahua_sdk import DahuaSDK
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hikvision_sdk():
    """Probar SDK de Hikvision"""
    print("🔍 Probando SDK de Hikvision...")
    
    try:
        sdk = HikvisionSDK()
        print("✅ Hikvision SDK cargado correctamente")
        return sdk
    except Exception as e:
        print(f"❌ Error Hikvision: {e}")
        return None

def test_dahua_sdk():
    """Probar SDK de Dahua"""
    print("🔍 Probando SDK de Dahua...")
    
    try:
        sdk = DahuaSDK()
        print("✅ Dahua SDK cargado correctamente")
        return sdk
    except Exception as e:
        print(f"❌ Error Dahua: {e}")
        return None

def test_device_connection(sdk, brand, ip, port, username, password):
    """Probar conexión a un dispositivo"""
    print(f"\n🌐 Probando conexión {brand} a {ip}:{port}...")
    
    try:
        result = sdk.login(ip, port, username, password)
        print(f"✅ Conexión {brand} exitosa!")
        print(f"   User ID: {result['user_id']}")
        
        if brand == "Hikvision":
            print(f"   Canales: {result['device_info']['channels']}")
            print(f"   Serial: {result['device_info']['serial_number']}")
        else:  # Dahua
            print(f"   Token: {result['token'][:20]}..." if result['token'] else "   Token: (vacío)")
            print(f"   Canales: {result['device_info']['channels']}")
        
        # Cerrar sesión
        sdk.logout(result['user_id'])
        print(f"✅ Sesión {brand} cerrada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión {brand}: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de ambos SDKs")
    print("=" * 60)
    
    # Probar carga de ambos SDKs
    hikvision_sdk = test_hikvision_sdk()
    dahua_sdk = test_dahua_sdk()
    
    if not hikvision_sdk and not dahua_sdk:
        print("❌ No se pudo cargar ningún SDK")
        return False
    
    # Configuración de dispositivos de prueba
    test_devices = []
    
    if hikvision_sdk:
        test_devices.append({
            "sdk": hikvision_sdk,
            "brand": "Hikvision",
            "ip": "192.168.1.100",
            "port": 8000,
            "username": "admin",
            "password": "admin123"
        })
    
    if dahua_sdk:
        test_devices.append({
            "sdk": dahua_sdk,
            "brand": "Dahua",
            "ip": "192.168.1.101",
            "port": 37777,
            "username": "admin",
            "password": "admin123"
        })
    
    print(f"\n📋 Configuración de dispositivos de prueba:")
    for device in test_devices:
        print(f"   {device['brand']}: {device['ip']}:{device['port']} ({device['username']})")
    
    # Preguntar si continuar con las pruebas de conexión
    response = input("\n¿Continuar con las pruebas de conexión? (s/n): ")
    if response.lower() != 's':
        print("⏭️ Saltando pruebas de conexión")
        return True
    
    # Probar conexiones
    results = {}
    for device in test_devices:
        connection_ok = test_device_connection(
            device['sdk'],
            device['brand'],
            device['ip'],
            device['port'],
            device['username'],
            device['password']
        )
        results[device['brand']] = connection_ok
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for brand, sdk in [("Hikvision", hikvision_sdk), ("Dahua", dahua_sdk)]:
        if sdk:
            print(f"✅ {brand} SDK: Cargado")
            if brand in results:
                print(f"✅ {brand} Conexión: {'OK' if results[brand] else 'FALLO'}")
            else:
                print(f"⏭️ {brand} Conexión: No probada")
        else:
            print(f"❌ {brand} SDK: No disponible")
    
    # Verificar si al menos un SDK funciona
    working_sdks = sum(1 for sdk in [hikvision_sdk, dahua_sdk] if sdk)
    working_connections = sum(1 for result in results.values() if result)
    
    if working_sdks > 0:
        print(f"\n🎉 {working_sdks} SDK(s) cargado(s) correctamente")
        if working_connections > 0:
            print(f"🎉 {working_connections} conexión(es) exitosa(s)")
        else:
            print("⚠️ Ninguna conexión exitosa (verificar configuración de dispositivos)")
        return True
    else:
        print("\n❌ No se pudo cargar ningún SDK")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
