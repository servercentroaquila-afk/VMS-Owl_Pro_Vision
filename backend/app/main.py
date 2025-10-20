from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .database import Base, engine
from .routes import devices, recordings, streams
from .auth import create_access_token, authenticate_user, verify_token
from .schemas import UserLogin, Token
from .stream_manager import StreamManager

# Crear tablas de la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar aplicación FastAPI
app = FastAPI(
    title="VMS Áquila API",
    description="Sistema de Gestión de Video (VMS) para cámaras Hikvision y Dahua",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio estático para archivos HLS
hls_root = os.getenv("HLS_ROOT", "/var/www/hls")
if os.path.exists(hls_root):
    app.mount("/hls", StaticFiles(directory=hls_root), name="hls")

# Inicializar gestor de streams
stream_manager = StreamManager()

# Rutas de autenticación
@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Iniciar sesión en el sistema"""
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me")
async def get_current_user(current_user: str = Depends(verify_token)):
    """Obtener información del usuario actual"""
    return {"username": current_user, "role": "admin"}

# Incluir routers
app.include_router(devices.router, prefix="/api")
app.include_router(recordings.router, prefix="/api")
app.include_router(streams.router, prefix="/api")

# Rutas de salud del sistema
@app.get("/api/health")
async def health_check():
    """Verificar estado del sistema"""
    try:
        # Verificar conexión a base de datos
        from .database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        
        # Obtener estadísticas de streams
        stream_stats = stream_manager.get_stream_stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "streams": {
                "active": stream_stats["active_streams"],
                "total_segments": stream_stats["total_segments"]
            },
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Sistema no disponible: {str(e)}"
        )

@app.get("/api/stats/overview")
async def get_system_overview(current_user: str = Depends(verify_token)):
    """Obtener resumen general del sistema"""
    try:
        from .database import SessionLocal
        from . import models
        
        db = SessionLocal()
        
        # Estadísticas de dispositivos
        total_devices = db.query(models.Device).count()
        active_devices = db.query(models.Device).filter(models.Device.is_active == True).count()
        hikvision_devices = db.query(models.Device).filter(models.Device.brand == "hikvision").count()
        dahua_devices = db.query(models.Device).filter(models.Device.brand == "dahua").count()
        
        # Estadísticas de streams
        stream_stats = stream_manager.get_stream_stats()
        
        # Estadísticas de grabaciones (últimas 24 horas)
        from datetime import datetime, timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_recordings = db.query(models.Recording).filter(
            models.Recording.created_at >= yesterday
        ).count()
        
        db.close()
        
        return {
            "devices": {
                "total": total_devices,
                "active": active_devices,
                "inactive": total_devices - active_devices,
                "by_brand": {
                    "hikvision": hikvision_devices,
                    "dahua": dahua_devices
                }
            },
            "streams": {
                "active": stream_stats["active_streams"],
                "total_segments": stream_stats["total_segments"]
            },
            "recordings": {
                "last_24h": recent_recordings
            },
            "system": {
                "version": "1.0.0",
                "status": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo resumen: {str(e)}"
        )

# Ruta raíz
@app.get("/")
async def root():
    """Ruta raíz de la API"""
    return {
        "message": "VMS Áquila API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }

# Manejo de errores global
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"detail": "Endpoint no encontrado"}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"detail": "Error interno del servidor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
