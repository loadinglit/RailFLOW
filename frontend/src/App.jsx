import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Login from './pages/Login'
import Signup from './pages/Signup'
import PassengerHome from './pages/PassengerHome'
import PoliceDashboard from './pages/PoliceDashboard'

function ProtectedRoute({ children, allowedRole }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-400 text-sm">Loading...</div>
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />
  if (allowedRole && user.role !== allowedRole) {
    return <Navigate to={user.role === 'police' ? '/police' : '/'} replace />
  }
  return children
}

function AppRoutes() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-400 text-sm">Loading...</div>
      </div>
    )
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={user ? <Navigate to={user.role === 'police' ? '/police' : '/'} replace /> : <Login />} />
      <Route path="/signup" element={user ? <Navigate to={user.role === 'police' ? '/police' : '/'} replace /> : <Signup />} />

      {/* Passenger — mobile-first home (trains + bot tabs) */}
      <Route path="/" element={<ProtectedRoute allowedRole="passenger"><PassengerHome /></ProtectedRoute>} />

      {/* Police — mobile-first dashboard */}
      <Route path="/police" element={<ProtectedRoute allowedRole="police"><PoliceDashboard /></ProtectedRoute>} />

      {/* Legacy /bot route → redirect to home */}
      <Route path="/bot" element={<Navigate to="/" replace />} />

      {/* Default redirect */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default function App() {
  const [tab, setTab] = useState("trains");
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [datetime, setDatetime] = useState(() => {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    return `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [selectedTrain, setSelectedTrain] = useState(null);
  const [detailTrain, setDetailTrain] = useState(null);
  const [error, setError] = useState("");

  // Bot state
  const [botMessages, setBotMessages] = useState([
    { role: "assistant", content: "Namaste! I'm Jan Suraksha Bot. If you faced a problem on a Mumbai local — overcrowding, harassment, injury, delay — I'll help you file a formal complaint and claim compensation. Tell me what happened." }
  ]);
  const [botInput, setBotInput] = useState("");
  const [botLoading, setBotLoading] = useState(false);
  const botRef = useRef();

  const swapStations = () => {
    const tmp = origin;
    setOrigin(destination);
    setDestination(tmp);
  };

  const handleSearch = async () => {
    if (!origin || !destination) { setError("Please enter both origin and destination."); return; }
    if (origin === destination) { setError("Origin and destination cannot be the same."); return; }
    setError("");
    setLoading(true);
    setResults(null);
    setDetailTrain(null);

    try {
      const res = await fetch("/api/trains/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin,
          destination,
          datetime_str: datetime.length === 16 ? datetime + ":00" : datetime,
        }),
      });
      const data = await res.json();
      setResults(data);
    } catch {
      setResults(getMockResults(origin, destination));
    } finally {
      setLoading(false);
    }
  };

  const sendBotMessage = async () => {
    if (!botInput.trim()) return;
    const msg = botInput.trim();
    setBotInput("");
    setBotMessages(prev => [...prev, { role: "user", content: msg }]);
    setBotLoading(true);

    try {
      const res = await fetch("/api/bot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "railflow_user",
          message: msg,
          language: "en",
        }),
      });
      const data = await res.json();
      const botMsg = {
        role: "assistant",
        content: data.response || "Processing your complaint...",
        options: data.options || null,
        complaint_draft: data.complaint_draft,
        authority: data.authority,
        compensation: data.compensation,
      };
      setBotMessages(prev => [...prev, botMsg]);
    } catch {
      setBotMessages(prev => [...prev, {
        role: "assistant",
        content: "I'm connecting to the grievance system. Please describe the incident — train number, station, and what happened."
      }]);
    } finally {
      setBotLoading(false);
      setTimeout(() => botRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    }
  };

  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
