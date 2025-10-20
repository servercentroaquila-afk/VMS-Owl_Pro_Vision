from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas, crud
from ..auth import verify_token
from ..stream_manager import StreamManager
from ..hikvision_sdk import HikvisionSDK
from ..dahua_sdk import DahuaSDK

router = APIRouter(prefix="/streams", tags=["streams"])

# Instancia global del gestor de streams
stream_manager = StreamManager()

@router.post("/start")
def start_stream(
    device_id: int,
    channel: int = Query(1, ge=1, le=64),
    sub_stream: int = Query(0, ge=0, le=1),
    duration: int = Query(3600, ge=60, le=86400),
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Iniciar un stream HLS desde un dispositivo"""
    device = crud.get_device(db, device_id=device_id)
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado"
        )
    
    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El dispositivo está inactivo"
        )
    
    try:
        # Generar URL RTSP según la marca del dispositivo
        if device.brand == "hikvision":
            sdk = HikvisionSDK()
            rtsp_url = sdk.get_rtsp_url(
                device.ip, device.port, device.username, 
                device.password, channel, sub_stream
            )
        elif device.brand == "dahua":
            sdk = DahuaSDK()
            rtsp_url = sdk.get_rtsp_url(
                device.ip, device.port, device.username, 
                device.password, channel, sub_stream
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marca de dispositivo no soportada"
            )
        
        # Iniciar stream HLS
        stream_id, playlist_url = stream_manager.start_hls(rtsp_url, duration=duration)
        
        # Guardar información del stream en la base de datos
        stream_data = schemas.StreamCreate(
            device_id=device_id,
            channel=channel,
            sub_stream=sub_stream,
            rtsp_url=rtsp_url,
            hls_url=playlist_url
        )
        stream_data.stream_id = stream_id
        crud.create_stream(db, stream_data)
        
        return {
            "stream_id": stream_id,
            "playlist_url": playlist_url,
            "device_id": device_id,
            "device_name": device.name,
            "channel": channel,
            "sub_stream": sub_stream,
            "duration": duration,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error iniciando stream: {str(e)}"
        )

@router.post("/stop")
def stop_stream(
    stream_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Detener un stream HLS"""
    try:
        # Detener el stream en el gestor
        success = stream_manager.stop_hls(stream_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stream no encontrado o ya detenido"
            )
        
        # Actualizar estado en la base de datos
        crud.stop_stream(db, stream_id)
        
        return {
            "stream_id": stream_id,
            "status": "stopped",
            "message": "Stream detenido correctamente"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deteniendo stream: {str(e)}"
        )

@router.get("/active")
def list_active_streams(
    current_user: str = Depends(verify_token)
):
    """Listar todos los streams activos"""
    try:
        streams = stream_manager.list_active_streams()
        return {
            "total_streams": len(streams),
            "streams": streams
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo streams activos: {str(e)}"
        )

@router.get("/{stream_id}")
def get_stream_info(
    stream_id: str,
    current_user: str = Depends(verify_token)
):
    """Obtener información de un stream específico"""
    try:
        stream_info = stream_manager.get_stream_info(stream_id)
        
        if stream_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stream no encontrado"
            )
        
        return {
            "stream_id": stream_id,
            "playlist_url": stream_info["playlist_url"],
            "started_at": stream_info["started_at"].isoformat(),
            "duration": stream_info["duration"],
            "rtsp_url": stream_info["rtsp_url"],
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información del stream: {str(e)}"
        )

@router.get("/stats/overview")
def get_stream_stats(
    current_user: str = Depends(verify_token)
):
    """Obtener estadísticas de streams"""
    try:
        stats = stream_manager.get_stream_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

@router.post("/bulk/start")
def start_multiple_streams(
    requests: List[dict],
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Iniciar múltiples streams simultáneamente"""
    results = []
    
    for req in requests:
        try:
            device_id = req.get("device_id")
            channel = req.get("channel", 1)
            sub_stream = req.get("sub_stream", 0)
            duration = req.get("duration", 3600)
            
            if not device_id:
                results.append({
                    "device_id": device_id,
                    "status": "error",
                    "message": "device_id es requerido"
                })
                continue
            
            # Iniciar stream individual
            result = start_stream(
                device_id=device_id,
                channel=channel,
                sub_stream=sub_stream,
                duration=duration,
                db=db,
                current_user=current_user
            )
            
            results.append({
                "device_id": device_id,
                "channel": channel,
                "status": "success",
                "stream_id": result["stream_id"],
                "playlist_url": result["playlist_url"]
            })
            
        except Exception as e:
            results.append({
                "device_id": req.get("device_id"),
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total_requests": len(requests),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }

@router.post("/bulk/stop")
def stop_multiple_streams(
    stream_ids: List[str],
    current_user: str = Depends(verify_token)
):
    """Detener múltiples streams simultáneamente"""
    results = []
    
    for stream_id in stream_ids:
        try:
            success = stream_manager.stop_hls(stream_id)
            results.append({
                "stream_id": stream_id,
                "status": "success" if success else "error",
                "message": "Stream detenido" if success else "Stream no encontrado"
            })
        except Exception as e:
            results.append({
                "stream_id": stream_id,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total_streams": len(stream_ids),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }
