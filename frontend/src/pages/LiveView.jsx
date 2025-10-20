import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import CameraTile from "../components/CameraTile";
import { 
  PlayIcon, 
  StopIcon, 
  PauseIcon,
  VideoCameraIcon,
  AdjustmentsHorizontalIcon
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

export default function LiveView() {
  const [searchParams] = useSearchParams();
  const [devices, setDevices] = useState([]);
  const [activeStreams, setActiveStreams] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [gridSize, setGridSize] = useState(8); // 8x8 = 64 cámaras
  const [autoStart, setAutoStart] = useState(false);

  useEffect(() => {
    loadDevices();
    loadActiveStreams();
  }, []);

  useEffect(() => {
    const deviceId = searchParams.get('device');
    if (deviceId) {
      setSelectedDevice(parseInt(deviceId));
    }
  }, [searchParams]);

  const loadDevices = async () => {
    try {
      const response = await axios.get('/api/devices');
      setDevices(response.data.filter(device => device.is_active));
    } catch (error) {
      console.error('Error cargando dispositivos:', error);
      toast.error('Error cargando dispositivos');
    } finally {
      setIsLoading(false);
    }
  };

  const loadActiveStreams = async () => {
    try {
      const response = await axios.get('/api/streams/active');
      setActiveStreams(response.data.streams);
    } catch (error) {
      console.error('Error cargando streams activos:', error);
    }
  };

  const startAllStreams = async () => {
    setIsLoading(true);
    try {
      const requests = devices.map(device => ({
        device_id: device.id,
        channel: 1,
        sub_stream: 0,
        duration: 3600
      }));

      const response = await axios.post('/api/streams/bulk/start', requests);
      
      toast.success(`${response.data.successful} streams iniciados correctamente`);
      loadActiveStreams();
      
    } catch (error) {
      console.error('Error iniciando streams:', error);
      toast.error('Error iniciando streams');
    } finally {
      setIsLoading(false);
    }
  };

  const stopAllStreams = async () => {
    setIsLoading(true);
    try {
      const streamIds = Object.keys(activeStreams);
      
      if (streamIds.length === 0) {
        toast.info('No hay streams activos');
        return;
      }

      const response = await axios.post('/api/streams/bulk/stop', streamIds);
      
      toast.success(`${response.data.successful} streams detenidos correctamente`);
      loadActiveStreams();
      
    } catch (error) {
      console.error('Error deteniendo streams:', error);
      toast.error('Error deteniendo streams');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStreamStart = (streamData) => {
    loadActiveStreams();
    toast.success(`Stream iniciado: ${streamData.device_name}`);
  };

  const handleStreamStop = (streamId) => {
    loadActiveStreams();
    toast.info('Stream detenido');
  };

  const getGridCols = () => {
    const sizes = { 4: 'grid-cols-4', 6: 'grid-cols-6', 8: 'grid-cols-8', 10: 'grid-cols-10' };
    return sizes[gridSize] || 'grid-cols-8';
  };

  const filteredDevices = selectedDevice 
    ? devices.filter(device => device.id === selectedDevice)
    : devices;

  if (isLoading && devices.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Vista en Vivo</h1>
            
            <div className="flex items-center space-x-4">
              {/* Grid Size Selector */}
              <div className="flex items-center space-x-2">
                <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-400" />
                <select
                  value={gridSize}
                  onChange={(e) => setGridSize(parseInt(e.target.value))}
                  className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                >
                  <option value={4}>4x4 (16 cámaras)</option>
                  <option value={6}>6x6 (36 cámaras)</option>
                  <option value={8}>8x8 (64 cámaras)</option>
                  <option value={10}>10x10 (100 cámaras)</option>
                </select>
              </div>

              {/* Device Filter */}
              <select
                value={selectedDevice || ''}
                onChange={(e) => setSelectedDevice(e.target.value ? parseInt(e.target.value) : null)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="">Todos los dispositivos</option>
                {devices.map(device => (
                  <option key={device.id} value={device.id}>
                    {device.name}
                  </option>
                ))}
              </select>

              {/* Control Buttons */}
              <div className="flex space-x-2">
                <button
                  onClick={startAllStreams}
                  disabled={isLoading || devices.length === 0}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PlayIcon className="h-4 w-4 mr-1" />
                  Iniciar Todos
                </button>
                
                <button
                  onClick={stopAllStreams}
                  disabled={isLoading || Object.keys(activeStreams).length === 0}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <StopIcon className="h-4 w-4 mr-1" />
                  Detener Todos
                </button>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-4 flex items-center space-x-6 text-sm text-gray-600">
            <span>Dispositivos: {devices.length}</span>
            <span>Streams activos: {Object.keys(activeStreams).length}</span>
            <span>Vista: {gridSize}x{gridSize}</span>
          </div>
        </div>
      </div>

      {/* Camera Grid */}
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {filteredDevices.length === 0 ? (
          <div className="text-center py-12">
            <VideoCameraIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No hay dispositivos</h3>
            <p className="mt-1 text-sm text-gray-500">
              No se encontraron dispositivos activos para mostrar.
            </p>
          </div>
        ) : (
          <div className={`grid ${getGridCols()} gap-2`}>
            {filteredDevices.map(device => (
              <CameraTile
                key={device.id}
                device={device}
                channel={1}
                subStream={0}
                onStreamStart={handleStreamStart}
                onStreamStop={handleStreamStop}
                className="h-48"
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer Info */}
      <div className="bg-white border-t border-gray-200 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            <p>
              VMS Áquila - Sistema de Gestión de Video | 
              Streams HLS en tiempo real | 
              Máximo {gridSize * gridSize} cámaras simultáneas
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
