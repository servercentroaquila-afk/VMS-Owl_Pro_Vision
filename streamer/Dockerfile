FROM ubuntu:22.04

# Instalar FFmpeg y dependencias
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar script de inicio
COPY start_stream.sh .
RUN chmod +x start_stream.sh

# Crear directorio para HLS
RUN mkdir -p /var/www/hls

# Crear usuario no-root
RUN useradd -m -u 1000 streamer && \
    chown -R streamer:streamer /app /var/www/hls

USER streamer

# Exponer puerto RTMP (opcional)
EXPOSE 1935

# Comando por defecto (mantener contenedor activo)
CMD ["tail", "-f", "/dev/null"]
