import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ChatBot from './pages/ChatBot'
import CrowdDashboard from './pages/CrowdDashboard'
import DisruptionView from './pages/DisruptionView'
import AlertPanel from './pages/AlertPanel'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/bot" replace />} />
          <Route path="/bot" element={<ChatBot />} />
          <Route path="/crowd" element={<CrowdDashboard />} />
          <Route path="/disruption" element={<DisruptionView />} />
          <Route path="/alerts" element={<AlertPanel />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
