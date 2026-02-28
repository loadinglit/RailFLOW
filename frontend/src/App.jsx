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
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
