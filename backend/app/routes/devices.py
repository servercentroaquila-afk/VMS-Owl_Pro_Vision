from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas, crud
from ..auth import verify_token

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("/", response_model=schemas.Device)
def create_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Crear un nuevo dispositivo"""
    try:
        # Verificar que no exista un dispositivo con la misma IP
        existing_device = db.query(models.Device).filter(
            models.Device.ip == device.ip,
            models.Device.port == device.port
        ).first()
        
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un dispositivo con esta IP y puerto"
            )
        
        return crud.create_device(db=db, device=device)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando dispositivo: {str(e)}"
        )

@router.get("/", response_model=List[schemas.Device])
def get_devices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Obtener lista de dispositivos"""
    devices = crud.get_devices(db, skip=skip, limit=limit)
    return devices

@router.get("/{device_id}", response_model=schemas.Device)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Obtener un dispositivo específico"""
    device = crud.get_device(db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    return device

@router.put("/{device_id}", response_model=schemas.Device)
def update_device(
    device_id: int,
    device_update: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Actualizar un dispositivo"""
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    return crud.update_device(db=db, device_id=device_id, device=device_update)

@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Eliminar un dispositivo"""
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    crud.delete_device(db=db, device_id=device_id)
    return {"message": "Dispositivo eliminado correctamente"}

@router.post("/{device_id}/test")
def test_device_connection(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Probar conexión a un dispositivo"""
    device = crud.get_device(db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    try:
        if device.brand == "hikvision":
            from ..hikvision_sdk import HikvisionSDK
            sdk = HikvisionSDK()
            result = sdk.login(device.ip, device.port, device.username, device.password)
            sdk.logout(result["user_id"])
            
        elif device.brand == "dahua":
            from ..dahua_sdk import DahuaSDK
            sdk = DahuaSDK()
            result = sdk.login(device.ip, device.port, device.username, device.password)
            sdk.logout(result["user_id"])
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marca de dispositivo no soportada"
            )
        
        return {
            "status": "success",
            "message": "Conexión exitosa",
            "device_info": result.get("device_info", {})
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de conexión: {str(e)}"
        )

@router.get("/{device_id}/channels")
def get_device_channels(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Obtener información de canales del dispositivo"""
    device = crud.get_device(db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    try:
        if device.brand == "hikvision":
            from ..hikvision_sdk import HikvisionSDK
            sdk = HikvisionSDK()
            result = sdk.login(device.ip, device.port, device.username, device.password)
            sdk.logout(result["user_id"])
            
        elif device.brand == "dahua":
            from ..dahua_sdk import DahuaSDK
            sdk = DahuaSDK()
            result = sdk.login(device.ip, device.port, device.username, device.password)
            sdk.logout(result["user_id"])
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marca de dispositivo no soportada"
            )
        
        channels = []
        total_channels = result.get("device_info", {}).get("channels", device.channels)
        
        for i in range(1, total_channels + 1):
            channels.append({
                "channel": i,
                "name": f"Canal {i}",
                "enabled": True,
                "rtsp_main": sdk.get_rtsp_url(device.ip, device.port, device.username, device.password, i, 0),
                "rtsp_sub": sdk.get_rtsp_url(device.ip, device.port, device.username, device.password, i, 1)
            })
        
        return {
            "device_id": device_id,
            "total_channels": total_channels,
            "channels": channels
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error obteniendo canales: {str(e)}"
        )
