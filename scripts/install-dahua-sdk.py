#!/usr/bin/env python3
"""
Script de instalación automática del SDK de Dahua
"""

import os
import shutil
import sys
from pathlib import Path

def install_dahua_sdk():
    """Instalar SDK de Dahua"""
    print("🚀 Instalando SDK de Dahua NetSDK v3.060...")
    
    # Directorios
    source_dir = Path("C:/Users/MonsterCat1998/Downloads/General_NetSDK_Eng_Win64_IS_V3.060.0000001.0.R.250812")
    target_dir = Path("backend/sdk/dahua")
    
    # Verificar directorio fuente
    if not source_dir.exists():
        print(f"❌ Directorio fuente no encontrado: {source_dir}")
        return False
    
    # Crear directorio destino
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Archivos a copiar
    files_to_copy = [
        # Librerías principales
        ("Bin/dhnetsdk.dll", "dhnetsdk.dll"),
        ("Bin/play.dll", "play.dll"),
        ("Bin/dhconfigsdk.dll", "dhconfigsdk.dll"),
        ("Bin/avnetsdk.dll", "avnetsdk.dll"),
        
        # Librerías de soporte
        ("Bin/libeay32.dll", "libeay32.dll"),
        ("Bin/ssleay32.dll", "ssleay32.dll"),
        ("Bin/Infra.dll", "Infra.dll"),
        ("Bin/RenderEngine.dll", "RenderEngine.dll"),
        ("Bin/IvsDrawer.dll", "IvsDrawer.dll"),
        ("Bin/StreamConvertor.dll", "StreamConvertor.dll"),
        
        # Headers
        ("Include/Common/dhnetsdk.h", "dhnetsdk.h"),
        ("Include/Common/dhconfigsdk.h", "dhconfigsdk.h"),
        ("Include/Common/avglobal.h", "avglobal.h"),
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
    success = install_dahua_sdk()
    sys.exit(0 if success else 1)
