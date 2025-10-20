import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LiveView from './pages/LiveView';
import Playback from './pages/Playback';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/live" element={<LiveView />} />
          <Route path="/playback" element={<Playback />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
