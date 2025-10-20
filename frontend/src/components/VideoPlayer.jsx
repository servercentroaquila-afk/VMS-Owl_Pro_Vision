import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";

export default function VideoPlayer({ 
  url, 
  className = "", 
  controls = true, 
  autoPlay = true,
  muted = true,
  onError = null,
  onLoadStart = null,
  onCanPlay = null
}) {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !url) return;

    setIsLoading(true);
    setHasError(false);
    setErrorMessage("");

    // Limpiar instancia HLS anterior
    if (hlsRef.current) {
      hlsRef.current.destroy();
      hlsRef.current = null;
    }

    if (Hls.isSupported()) {
      // Usar HLS.js para streams HLS
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90
      });
      
      hlsRef.current = hls;

      hls.on(Hls.Events.MEDIA_ATTACHED, () => {
        console.log("HLS: Media attached");
        if (onLoadStart) onLoadStart();
      });

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log("HLS: Manifest parsed");
        if (autoPlay) {
          video.play().catch(e => console.log("Autoplay prevented:", e));
        }
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error("HLS Error:", data);
        setHasError(true);
        setErrorMessage(`Error HLS: ${data.type} - ${data.details}`);
        setIsLoading(false);
        if (onError) onError(data);
      });

      hls.loadSource(url);
      hls.attachMedia(video);

    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // Safari nativo
      video.src = url;
      if (autoPlay) {
        video.play().catch(e => console.log("Autoplay prevented:", e));
      }
    } else {
      setHasError(true);
      setErrorMessage("HLS no soportado en este navegador");
      setIsLoading(false);
    }

    // Eventos del video
    const handleCanPlay = () => {
      setIsLoading(false);
      if (onCanPlay) onCanPlay();
    };

    const handleError = (e) => {
      console.error("Video error:", e);
      setHasError(true);
      setErrorMessage("Error cargando video");
      setIsLoading(false);
      if (onError) onError(e);
    };

    const handleLoadStart = () => {
      setIsLoading(true);
      if (onLoadStart) onLoadStart();
    };

    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('error', handleError);
    video.addEventListener('loadstart', handleLoadStart);

    return () => {
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('error', handleError);
      video.removeEventListener('loadstart', handleLoadStart);
      
      if (hlsRef.current) {
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };
  }, [url, autoPlay, onError, onLoadStart, onCanPlay]);

  if (hasError) {
    return (
      <div className={`bg-gray-800 text-white flex items-center justify-center ${className}`}>
        <div className="text-center p-4">
          <div className="text-red-400 mb-2">⚠️</div>
          <div className="text-sm">{errorMessage}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative bg-black ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 z-10">
          <div className="text-white text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
            <div className="text-sm">Cargando...</div>
          </div>
        </div>
      )}
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        controls={controls}
        muted={muted}
        playsInline
        preload="metadata"
      />
    </div>
  );
}
