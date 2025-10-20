import { useState, useEffect } from "react";
import axios from "axios";
import VideoPlayer from "./VideoPlayer";
import { PlayIcon, StopIcon, PauseIcon } from "@heroicons/react/24/solid";

export default function CameraTile({ 
  device, 
  channel = 1, 
  subStream = 0,
  className = "",
  onStreamStart = null,
  onStreamStop = null
}) {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamId, setStreamId] = useState(null);
  const [playlistUrl, setPlaylistUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const startStream = async () => {
    if (isStreaming) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/streams/start', {
        device_id: device.id,
        channel: channel,
        sub_stream: subStream,
        duration: 3600 // 1 hora
      });
      
      setStreamId(response.data.stream_id);
      setPlaylistUrl(response.data.playlist_url);
      setIsStreaming(true);
      
      if (onStreamStart) {
        onStreamStart(response.data);
      }
      
    } catch (err) {
      console.error('Error iniciando stream:', err);
      setError(err.response?.data?.detail || 'Error iniciando stream');
    } finally {
      setIsLoading(false);
    }
  };

  const stopStream = async () => {
    if (!isStreaming || !streamId) return;
    
    setIsLoading(true);
    
    try {
      await axios.post('/api/streams/stop', {
        stream_id: streamId
      });
      
      setStreamId(null);
      setPlaylistUrl(null);
      setIsStreaming(false);
      
      if (onStreamStop) {
        onStreamStop(streamId);
      }
      
    } catch (err) {
      console.error('Error deteniendo stream:', err);
      setError(err.response?.data?.detail || 'Error deteniendo stream');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVideoError = (error) => {
    console.error('Video error:', error);
    setError('Error reproduciendo video');
  };

  const handleVideoCanPlay = () => {
    setError(null);
  };

  return (
    <div className={`bg-gray-900 text-white rounded-lg overflow-hidden shadow-lg ${className}`}>
      {/* Header */}
      <div className="bg-gray-800 px-3 py-2 flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium truncate">
            {device.name} - Ch{channel}
          </h3>
          <p className="text-xs text-gray-400">
            {device.brand.toUpperCase()} • {device.ip}
          </p>
        </div>
        
        <div className="flex items-center space-x-1">
          {!isStreaming ? (
            <button
              onClick={startStream}
              disabled={isLoading}
              className="p-1.5 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded transition-colors"
              title="Iniciar stream"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <PlayIcon className="h-4 w-4" />
              )}
            </button>
          ) : (
            <button
              onClick={stopStream}
              disabled={isLoading}
              className="p-1.5 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded transition-colors"
              title="Detener stream"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <StopIcon className="h-4 w-4" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Video Area */}
      <div className="relative aspect-video bg-black">
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <div className="text-center p-4">
              <div className="text-red-400 mb-2">⚠️</div>
              <div className="text-sm text-gray-300">{error}</div>
              <button
                onClick={() => setError(null)}
                className="mt-2 text-xs text-blue-400 hover:text-blue-300"
              >
                Reintentar
              </button>
            </div>
          </div>
        ) : playlistUrl ? (
          <VideoPlayer
            url={playlistUrl}
            className="w-full h-full"
            onError={handleVideoError}
            onCanPlay={handleVideoCanPlay}
            controls={false}
            autoPlay={true}
            muted={true}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <div className="text-center">
              <div className="text-gray-400 mb-2">📹</div>
              <div className="text-sm text-gray-300">Presiona play para iniciar</div>
            </div>
          </div>
        )}
      </div>

      {/* Status */}
      <div className="px-3 py-2 bg-gray-800 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs">
          <span className={`px-2 py-1 rounded ${
            isStreaming ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
          }`}>
            {isStreaming ? 'EN VIVO' : 'OFFLINE'}
          </span>
          {streamId && (
            <span className="text-gray-400 truncate ml-2">
              ID: {streamId.substring(0, 8)}...
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
