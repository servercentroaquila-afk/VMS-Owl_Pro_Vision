from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from .. import models, schemas, crud
from ..auth import verify_token

router = APIRouter(prefix="/recordings", tags=["recordings"])

@router.get("/{device_id}")
def list_recordings(
    device_id: int,
    start: str = Query(..., description="Fecha de inicio (YYYY-MM-DD HH:MM:SS)"),
    end: str = Query(..., description="Fecha de fin (YYYY-MM-DD HH:MM:SS)"),
    channel: int = Query(1, ge=1, le=64, description="Canal a consultar"),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Obtener lista de grabaciones de un dispositivo"""
    device = crud.get_device(db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    try:
        # Validar formato de fechas
        start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        # Obtener grabaciones usando el SDK correspondiente
        if device.brand == "hikvision":
            from ..hikvision_sdk import HikvisionSDK
            sdk = HikvisionSDK()
            login_result = sdk.login(device.ip, device.port, device.username, device.password)
            recordings = sdk.find_recordings(login_result["user_id"], channel, start, end)
            sdk.logout(login_result["user_id"])
            
        elif device.brand == "dahua":
            from ..dahua_sdk import DahuaSDK
            sdk = DahuaSDK()
            login_result = sdk.login(device.ip, device.port, device.username, device.password)
            recordings = sdk.find_recordings(login_result["user_id"], channel, start, end)
            sdk.logout(login_result["user_id"])
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marca de dispositivo no soportada"
            )
        
        return {
            "device_id": device_id,
            "device_name": device.name,
            "channel": channel,
            "start_time": start,
            "end_time": end,
            "total_recordings": len(recordings),
            "recordings": recordings
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de fecha inválido: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo grabaciones: {str(e)}"
        )

@router.get("/{device_id}/channels/{channel}")
def get_channel_recordings(
    device_id: int,
    channel: int,
    start: str = Query(..., description="Fecha de inicio (YYYY-MM-DD HH:MM:SS)"),
    end: str = Query(..., description="Fecha de fin (YYYY-MM-DD HH:MM:SS)"),
    recording_type: str = Query("normal", regex="^(normal|alarm|motion)$"),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Obtener grabaciones de un canal específico con filtro de tipo"""
    device = crud.get_device(db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    try:
        # Validar formato de fechas
        start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        # Obtener grabaciones usando el SDK correspondiente
        if device.brand == "hikvision":
            from ..hikvision_sdk import HikvisionSDK
            sdk = HikvisionSDK()
            login_result = sdk.login(device.ip, device.port, device.username, device.password)
            recordings = sdk.find_recordings(login_result["user_id"], channel, start, end)
            sdk.logout(login_result["user_id"])
            
        elif device.brand == "dahua":
            from ..dahua_sdk import DahuaSDK
            sdk = DahuaSDK()
            login_result = sdk.login(device.ip, device.port, device.username, device.password)
            recordings = sdk.find_recordings(login_result["user_id"], channel, start, end)
            sdk.logout(login_result["user_id"])
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marca de dispositivo no soportada"
            )
        
        # Filtrar por tipo de grabación si es necesario
        if recording_type != "normal":
            recordings = [r for r in recordings if r.get("type") == recording_type]
        
        return {
            "device_id": device_id,
            "device_name": device.name,
            "channel": channel,
            "recording_type": recording_type,
            "start_time": start,
            "end_time": end,
            "total_recordings": len(recordings),
            "recordings": recordings
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de fecha inválido: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo grabaciones: {str(e)}"
        )

@router.post("/{device_id}/channels/{channel}/download")
def download_recording(
    device_id: int,
    channel: int,
    start: str = Query(..., description="Fecha de inicio (YYYY-MM-DD HH:MM:SS)"),
    end: str = Query(..., description="Fecha de fin (YYYY-MM-DD HH:MM:SS)"),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Iniciar descarga de una grabación específica"""
    device = crud.get_device(db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    try:
        # Validar formato de fechas
        start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        # En una implementación real, aquí se iniciaría la descarga
        # Por ahora, devolvemos información de la grabación solicitada
        return {
            "device_id": device_id,
            "device_name": device.name,
            "channel": channel,
            "start_time": start,
            "end_time": end,
            "download_url": f"/api/recordings/{device_id}/channels/{channel}/download?start={start}&end={end}",
            "status": "pending",
            "message": "Descarga iniciada. Use el download_url para obtener el archivo."
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de fecha inválido: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error iniciando descarga: {str(e)}"
        )

@router.get("/stats/summary")
def get_recordings_stats(
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Obtener estadísticas generales de grabaciones"""
    try:
        # Obtener estadísticas básicas
        total_devices = db.query(models.Device).count()
        active_devices = db.query(models.Device).filter(models.Device.is_active == True).count()
        
        # Obtener estadísticas por marca
        hikvision_count = db.query(models.Device).filter(models.Device.brand == "hikvision").count()
        dahua_count = db.query(models.Device).filter(models.Device.brand == "dahua").count()
        
        return {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "inactive_devices": total_devices - active_devices,
            "by_brand": {
                "hikvision": hikvision_count,
                "dahua": dahua_count
            },
            "total_channels": sum(device.channels for device in db.query(models.Device).all())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )
