#!/usr/bin/env python3
"""
Script de instalación automática del SDK de Hikvision
"""

import os
import shutil
import sys
from pathlib import Path

def install_hikvision_sdk():
    """Instalar SDK de Hikvision"""
    print("🚀 Instalando SDK de Hikvision v6.1.9.48...")
    
    # Directorios
    source_dir = Path("C:/Users/MonsterCat1998/Downloads/EN-HCNetSDKV6.1.9.48_build20230410_win64/EN-HCNetSDKV6.1.9.48_build20230410_win64")
    target_dir = Path("backend/sdk/hikvision")
    
    # Verificar directorio fuente
    if not source_dir.exists():
        print(f"❌ Directorio fuente no encontrado: {source_dir}")
        return False
    
    # Crear directorio destino
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Archivos a copiar
    files_to_copy = [
        ("lib/HCNetSDK.dll", "HCNetSDK.dll"),
        ("lib/PlayCtrl.dll", "PlayCtrl.dll"),
        ("lib/AudioRender.dll", "AudioRender.dll"),
        ("lib/HCCore.dll", "HCCore.dll"),
        ("lib/libcrypto-1_1-x64.dll", "libcrypto-1_1-x64.dll"),
        ("lib/libssl-1_1-x64.dll", "libssl-1_1-x64.dll"),
        ("lib/zlib1.dll", "zlib1.dll"),
        ("lib/OpenAL32.dll", "OpenAL32.dll"),
        ("incEn/HCNetSDK.h", "HCNetSDK.h"),
        ("incEn/DataType.h", "DataType.h"),
    ]
    
    # Copiar archivos
    for source_path, target_name in files_to_copy:
        source_file = source_dir / source_path
        target_file = target_dir / target_name
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            print(f"✅ Copiado: {target_name}")
        else:
            print(f"⚠️ No encontrado: {source_path}")
    
    print(f"\n✅ SDK instalado en: {target_dir.absolute()}")
    return True

if __name__ == "__main__":
    success = install_hikvision_sdk()
    sys.exit(0 if success else 1)
