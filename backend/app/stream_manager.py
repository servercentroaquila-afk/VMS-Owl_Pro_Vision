import subprocess
import os
import shlex
import uuid
import threading
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

HLS_ROOT = os.getenv("HLS_ROOT", "/var/www/hls")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

class StreamManager:
    def __init__(self):
        self.hls_root = Path(HLS_ROOT)
        self.hls_root.mkdir(parents=True, exist_ok=True)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.stream_info: Dict[str, Dict] = {}
        self.cleanup_thread = threading.Thread(target=self._cleanup_old_streams, daemon=True)
        self.cleanup_thread.start()

    def start_hls(self, rtsp_url: str, stream_id: str = None, duration: int = 3600) -> Tuple[str, str]:
        """
        Iniciar stream HLS desde RTSP
        
        Args:
            rtsp_url: URL RTSP de origen
            stream_id: ID único del stream (se genera si no se proporciona)
            duration: Duración máxima en segundos
            
        Returns:
            Tuple (stream_id, playlist_url)
        """
        if not stream_id:
            stream_id = str(uuid.uuid4())
        
        # Verificar si ya existe un stream activo
        if stream_id in self.processes:
            logger.warning(f"Stream {stream_id} ya está activo")
            return stream_id, self.stream_info[stream_id]["playlist_url"]
        
        try:
            # Crear directorio para el stream
            stream_dir = self.hls_root / stream_id
            stream_dir.mkdir(parents=True, exist_ok=True)
            
            playlist_path = stream_dir / "stream.m3u8"
            
            # Comando FFmpeg para HLS
            cmd = [
                FFMPEG_PATH,
                "-rtsp_transport", "tcp",
                "-i", rtsp_url,
                "-c:v", "copy",  # Copiar video sin re-encoding
                "-c:a", "aac",   # Re-encoding de audio a AAC
                "-f", "hls",
                "-hls_time", "4",           # Duración de cada segmento (4 segundos)
                "-hls_list_size", "5",      # Mantener 5 segmentos en la playlist
                "-hls_flags", "delete_segments",  # Eliminar segmentos antiguos
                "-hls_segment_filename", str(stream_dir / "segment_%03d.ts"),
                "-t", str(duration),        # Duración máxima
                str(playlist_path)
            ]
            
            logger.info(f"Iniciando stream {stream_id} con comando: {' '.join(cmd)}")
            
            # Iniciar proceso FFmpeg
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(stream_dir)
            )
            
            # Guardar información del proceso
            self.processes[stream_id] = proc
            self.stream_info[stream_id] = {
                "process": proc,
                "rtsp_url": rtsp_url,
                "playlist_url": f"/hls/{stream_id}/stream.m3u8",
                "started_at": datetime.utcnow(),
                "duration": duration,
                "stream_dir": str(stream_dir)
            }
            
            # Iniciar thread para monitorear el proceso
            monitor_thread = threading.Thread(
                target=self._monitor_stream,
                args=(stream_id,),
                daemon=True
            )
            monitor_thread.start()
            
            logger.info(f"Stream {stream_id} iniciado correctamente")
            return stream_id, self.stream_info[stream_id]["playlist_url"]
            
        except Exception as e:
            logger.error(f"Error iniciando stream {stream_id}: {e}")
            raise

    def stop_hls(self, stream_id: str) -> bool:
        """
        Detener stream HLS
        
        Args:
            stream_id: ID del stream a detener
            
        Returns:
            True si se detuvo correctamente
        """
        try:
            if stream_id not in self.processes:
                logger.warning(f"Stream {stream_id} no encontrado")
                return False
            
            proc = self.processes[stream_id]
            
            # Terminar proceso
            proc.terminate()
            
            # Esperar hasta 5 segundos para que termine gracefully
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Si no termina, forzar kill
                proc.kill()
                proc.wait()
            
            # Limpiar información
            del self.processes[stream_id]
            if stream_id in self.stream_info:
                del self.stream_info[stream_id]
            
            logger.info(f"Stream {stream_id} detenido correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error deteniendo stream {stream_id}: {e}")
            return False

    def get_stream_info(self, stream_id: str) -> Optional[Dict]:
        """Obtener información de un stream"""
        return self.stream_info.get(stream_id)

    def list_active_streams(self) -> Dict[str, Dict]:
        """Listar todos los streams activos"""
        return {
            stream_id: {
                "playlist_url": info["playlist_url"],
                "started_at": info["started_at"].isoformat(),
                "duration": info["duration"],
                "rtsp_url": info["rtsp_url"]
            }
            for stream_id, info in self.stream_info.items()
        }

    def _monitor_stream(self, stream_id: str):
        """Monitorear un stream en background"""
        try:
            proc = self.processes.get(stream_id)
            if not proc:
                return
            
            # Esperar a que termine el proceso
            return_code = proc.wait()
            
            logger.info(f"Stream {stream_id} terminó con código {return_code}")
            
            # Limpiar si el proceso terminó
            if stream_id in self.processes:
                del self.processes[stream_id]
            if stream_id in self.stream_info:
                del self.stream_info[stream_id]
                
        except Exception as e:
            logger.error(f"Error monitoreando stream {stream_id}: {e}")

    def _cleanup_old_streams(self):
        """Limpiar streams antiguos en background"""
        while True:
            try:
                current_time = datetime.utcnow()
                streams_to_remove = []
                
                for stream_id, info in self.stream_info.items():
                    # Eliminar streams que han excedido su duración
                    if current_time - info["started_at"] > timedelta(seconds=info["duration"]):
                        streams_to_remove.append(stream_id)
                
                # Eliminar streams marcados
                for stream_id in streams_to_remove:
                    logger.info(f"Limpiando stream expirado: {stream_id}")
                    self.stop_hls(stream_id)
                
                # Limpiar directorios vacíos
                self._cleanup_empty_directories()
                
                # Esperar 60 segundos antes de la siguiente limpieza
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error en limpieza de streams: {e}")
                time.sleep(60)

    def _cleanup_empty_directories(self):
        """Eliminar directorios vacíos de streams"""
        try:
            for stream_dir in self.hls_root.iterdir():
                if stream_dir.is_dir() and not any(stream_dir.iterdir()):
                    stream_dir.rmdir()
                    logger.debug(f"Directorio vacío eliminado: {stream_dir}")
        except Exception as e:
            logger.error(f"Error limpiando directorios: {e}")

    def get_stream_stats(self) -> Dict:
        """Obtener estadísticas de streams"""
        active_count = len(self.processes)
        total_segments = 0
        
        # Contar segmentos totales
        for stream_dir in self.hls_root.iterdir():
            if stream_dir.is_dir():
                segments = list(stream_dir.glob("*.ts"))
                total_segments += len(segments)
        
        return {
            "active_streams": active_count,
            "total_segments": total_segments,
            "hls_root": str(self.hls_root),
            "streams": self.list_active_streams()
        }

    def __del__(self):
        """Cleanup al destruir la instancia"""
        try:
            # Detener todos los streams activos
            for stream_id in list(self.processes.keys()):
                self.stop_hls(stream_id)
        except:
            pass
