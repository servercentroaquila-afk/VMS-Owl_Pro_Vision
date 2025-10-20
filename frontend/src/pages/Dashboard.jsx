import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { 
  VideoCameraIcon, 
  PlayIcon, 
  ClockIcon,
  DevicePhoneMobileIcon,
  ChartBarIcon
} from "@heroicons/react/24/outline";

export default function Dashboard() {
  const [stats, setStats] = useState({
    devices: { total: 0, active: 0 },
    streams: { active: 0 },
    recordings: { last_24h: 0 }
  });
  const [devices, setDevices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsResponse, devicesResponse] = await Promise.all([
        axios.get('/api/stats/overview'),
        axios.get('/api/devices')
      ]);
      
      setStats(statsResponse.data);
      setDevices(devicesResponse.data);
    } catch (error) {
      console.error('Error cargando datos del dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color = "blue" }) => (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className="text-lg font-medium text-gray-900">
                {value}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
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
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <div className="flex space-x-4">
              <Link
                to="/live"
                className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Vista en Vivo
              </Link>
              <Link
                to="/playback"
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Reproducción
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <StatCard
            title="Dispositivos Totales"
            value={stats.devices.total}
            icon={VideoCameraIcon}
            color="blue"
          />
          <StatCard
            title="Dispositivos Activos"
            value={stats.devices.active}
            icon={DevicePhoneMobileIcon}
            color="green"
          />
          <StatCard
            title="Streams Activos"
            value={stats.streams.active}
            icon={PlayIcon}
            color="purple"
          />
          <StatCard
            title="Grabaciones (24h)"
            value={stats.recordings.last_24h}
            icon={ClockIcon}
            color="orange"
          />
        </div>

        {/* Devices Table */}
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Dispositivos
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Lista de todos los dispositivos registrados en el sistema
            </p>
          </div>
          
          {devices.length === 0 ? (
            <div className="text-center py-12">
              <VideoCameraIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No hay dispositivos</h3>
              <p className="mt-1 text-sm text-gray-500">
                Comienza agregando un dispositivo al sistema.
              </p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {devices.map((device) => (
                <li key={device.id}>
                  <div className="px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className={`h-3 w-3 rounded-full ${
                          device.is_active ? 'bg-green-400' : 'bg-red-400'
                        }`} />
                      </div>
                      <div className="ml-4">
                        <div className="flex items-center">
                          <p className="text-sm font-medium text-gray-900">
                            {device.name}
                          </p>
                          <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                            {device.brand.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-sm text-gray-500">
                          {device.ip}:{device.port} • {device.channels} canales
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Link
                        to={`/live?device=${device.id}`}
                        className="text-primary-600 hover:text-primary-900 text-sm font-medium"
                      >
                        Ver en vivo
                      </Link>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-3">
          <Link
            to="/live"
            className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <div>
              <span className="rounded-lg inline-flex p-3 bg-primary-50 text-primary-600 ring-4 ring-white">
                <PlayIcon className="h-6 w-6" />
              </span>
            </div>
            <div className="mt-8">
              <h3 className="text-lg font-medium">
                <span className="absolute inset-0" aria-hidden="true" />
                Vista en Vivo
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Visualiza todas las cámaras en tiempo real
              </p>
            </div>
          </Link>

          <Link
            to="/playback"
            className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <div>
              <span className="rounded-lg inline-flex p-3 bg-primary-50 text-primary-600 ring-4 ring-white">
                <ClockIcon className="h-6 w-6" />
              </span>
            </div>
            <div className="mt-8">
              <h3 className="text-lg font-medium">
                <span className="absolute inset-0" aria-hidden="true" />
                Reproducción
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Reproduce grabaciones históricas
              </p>
            </div>
          </Link>

          <div className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg shadow hover:shadow-md transition-shadow">
            <div>
              <span className="rounded-lg inline-flex p-3 bg-primary-50 text-primary-600 ring-4 ring-white">
                <ChartBarIcon className="h-6 w-6" />
              </span>
            </div>
            <div className="mt-8">
              <h3 className="text-lg font-medium">
                <span className="absolute inset-0" aria-hidden="true" />
                Estadísticas
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Análisis y reportes del sistema
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
