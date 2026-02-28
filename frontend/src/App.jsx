import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ChatBot from './pages/ChatBot'
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
    return <Navigate to={user.role === 'police' ? '/police' : '/bot'} replace />
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
      <Route path="/login" element={user ? <Navigate to={user.role === 'police' ? '/police' : '/bot'} replace /> : <Login />} />
      <Route path="/signup" element={user ? <Navigate to={user.role === 'police' ? '/police' : '/bot'} replace /> : <Signup />} />

      {/* Protected routes inside Layout */}
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/bot" element={<ProtectedRoute allowedRole="passenger"><ChatBot /></ProtectedRoute>} />
        <Route path="/police" element={<ProtectedRoute allowedRole="police"><PoliceDashboard /></ProtectedRoute>} />
      </Route>

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