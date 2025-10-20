import { useState, useEffect } from "react";
import axios from "axios";
import VideoPlayer from "../components/VideoPlayer";
import { 
  CalendarIcon, 
  ClockIcon, 
  VideoCameraIcon,
  PlayIcon,
  MagnifyingGlassIcon
} from "@heroicons/react/24/outline";
import { format, subDays } from "date-fns";
import toast from "react-hot-toast";

export default function Playback() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [selectedChannel, setSelectedChannel] = useState(1);
  const [startDate, setStartDate] = useState(format(subDays(new Date(), 1), 'yyyy-MM-dd'));
  const [startTime, setStartTime] = useState('00:00');
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [endTime, setEndTime] = useState('23:59');
  const [recordings, setRecordings] = useState([]);
  const [selectedRecording, setSelectedRecording] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    try {
      const response = await axios.get('/api/devices');
      setDevices(response.data.filter(device => device.is_active));
      if (response.data.length > 0) {
        setSelectedDevice(response.data[0].id);
      }
    } catch (error) {
      console.error('Error cargando dispositivos:', error);
      toast.error('Error cargando dispositivos');
    }
  };

  const searchRecordings = async () => {
    if (!selectedDevice) {
      toast.error('Selecciona un dispositivo');
      return;
    }

    setIsSearching(true);
    try {
      const startDateTime = `${startDate} ${startTime}:00`;
      const endDateTime = `${endDate} ${endTime}:00`;

      const response = await axios.get(`/api/recordings/${selectedDevice}`, {
        params: {
          start: startDateTime,
          end: endDateTime,
          channel: selectedChannel
        }
      });

      setRecordings(response.data.recordings);
      
      if (response.data.recordings.length === 0) {
        toast.info('No se encontraron grabaciones en el rango seleccionado');
      } else {
        toast.success(`${response.data.recordings.length} grabaciones encontradas`);
      }

    } catch (error) {
      console.error('Error buscando grabaciones:', error);
      toast.error('Error buscando grabaciones');
    } finally {
      setIsSearching(false);
    }
  };

  const playRecording = (recording) => {
    setSelectedRecording(recording);
    toast.success(`Reproduciendo: ${recording.start} - ${recording.end}`);
  };

  const getSelectedDevice = () => {
    return devices.find(device => device.id === selectedDevice);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Reproducción de Grabaciones</h1>
          <p className="mt-2 text-sm text-gray-600">
            Busca y reproduce grabaciones históricas de tus cámaras
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Search Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Buscar Grabaciones
              </h3>

              <div className="space-y-4">
                {/* Device Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Dispositivo
                  </label>
                  <select
                    value={selectedDevice || ''}
                    onChange={(e) => setSelectedDevice(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Seleccionar dispositivo</option>
                    {devices.map(device => (
                      <option key={device.id} value={device.id}>
                        {device.name} ({device.brand.toUpperCase()})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Channel Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Canal
                  </label>
                  <select
                    value={selectedChannel}
                    onChange={(e) => setSelectedChannel(parseInt(e.target.value))}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {Array.from({ length: 16 }, (_, i) => i + 1).map(channel => (
                      <option key={channel} value={channel}>
                        Canal {channel}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Date Range */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fecha Inicio
                    </label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Hora Inicio
                    </label>
                    <input
                      type="time"
                      value={startTime}
                      onChange={(e) => setStartTime(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Fecha Fin
                    </label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Hora Fin
                    </label>
                    <input
                      type="time"
                      value={endTime}
                      onChange={(e) => setEndTime(e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>

                {/* Search Button */}
                <button
                  onClick={searchRecordings}
                  disabled={isSearching || !selectedDevice}
                  className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSearching ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  ) : (
                    <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                  )}
                  Buscar Grabaciones
                </button>
              </div>
            </div>
          </div>

          {/* Results and Player */}
          <div className="lg:col-span-2">
            {/* Video Player */}
            {selectedRecording && (
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Reproduciendo Grabación
                </h3>
                <div className="aspect-video bg-black rounded-lg overflow-hidden">
                  <VideoPlayer
                    url={selectedRecording.file_path || '/api/recordings/placeholder'}
                    className="w-full h-full"
                    controls={true}
                    autoPlay={false}
                    muted={false}
                  />
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  <p><strong>Dispositivo:</strong> {getSelectedDevice()?.name}</p>
                  <p><strong>Canal:</strong> {selectedChannel}</p>
                  <p><strong>Inicio:</strong> {selectedRecording.start}</p>
                  <p><strong>Fin:</strong> {selectedRecording.end}</p>
                  <p><strong>Tipo:</strong> {selectedRecording.type}</p>
                </div>
              </div>
            )}

            {/* Recordings List */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  Grabaciones Encontradas ({recordings.length})
                </h3>
              </div>

              {recordings.length === 0 ? (
                <div className="text-center py-12">
                  <VideoCameraIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">
                    No hay grabaciones
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Realiza una búsqueda para encontrar grabaciones.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {recordings.map((recording, index) => (
                    <div key={index} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                            <span className="text-sm font-medium text-gray-900">
                              {recording.start} - {recording.end}
                            </span>
                            <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {recording.type}
                            </span>
                          </div>
                          <div className="mt-1 text-sm text-gray-500">
                            Canal {recording.channel} • 
                            {recording.file_size && ` ${Math.round(recording.file_size / 1024 / 1024)} MB`}
                          </div>
                        </div>
                        <button
                          onClick={() => playRecording(recording)}
                          className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                        >
                          <PlayIcon className="h-4 w-4 mr-1" />
                          Reproducir
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
