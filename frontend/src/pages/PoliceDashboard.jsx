import { useState, useEffect } from 'react'
import { jsPDF } from 'jspdf'
import { Capacitor } from '@capacitor/core'
import { Filesystem, Directory } from '@capacitor/filesystem'
import { Share } from '@capacitor/share'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const STATUS_COLORS = {
  filed: 'bg-red-100 text-red-800',
  acknowledged: 'bg-amber-100 text-amber-800',
  resolved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-gray-200 text-gray-700',
}

const SEVERITY_COLORS = {
  low: 'bg-blue-100 text-blue-800',
  medium: 'bg-amber-100 text-amber-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
}

// ── SVG Mini Icons ──────────────────────────────────────────────
const MiniShield   = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
const MiniAlert    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
const MiniUser     = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
const MiniClock    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
const MiniTrain    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><rect x="4" y="3" width="16" height="13" rx="2"/><path d="M8 19h8M12 16v3M4 10h16"/></svg>
const MiniFile     = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
const MiniUsers    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
const MiniZap      = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>

const INCIDENT_CONFIG = {
  theft:              { icon: MiniShield, bg: 'bg-red-100',    text: 'text-red-700' },
  robbery:            { icon: MiniAlert,  bg: 'bg-red-100',    text: 'text-red-700' },
  assault:            { icon: MiniZap,    bg: 'bg-orange-100', text: 'text-orange-700' },
  sexual_harassment:  { icon: MiniAlert,  bg: 'bg-red-100',    text: 'text-red-700' },
  accident:           { icon: MiniTrain,  bg: 'bg-amber-100',  text: 'text-amber-700' },
  falling:            { icon: MiniAlert,  bg: 'bg-amber-100',  text: 'text-amber-700' },
  death:              { icon: MiniAlert,  bg: 'bg-red-100',    text: 'text-red-700' },
  platform_gap:       { icon: MiniAlert,  bg: 'bg-amber-100',  text: 'text-amber-700' },
  overcrowding:       { icon: MiniUsers,  bg: 'bg-blue-100',   text: 'text-blue-700' },
  delay:              { icon: MiniClock,  bg: 'bg-blue-100',   text: 'text-blue-700' },
  nuisance:           { icon: MiniAlert,  bg: 'bg-gray-100',   text: 'text-gray-600' },
  chain_pulling:      { icon: MiniTrain,  bg: 'bg-amber-100',  text: 'text-amber-700' },
  corruption:         { icon: MiniFile,   bg: 'bg-purple-100', text: 'text-purple-700' },
  staff_misconduct:   { icon: MiniUser,   bg: 'bg-purple-100', text: 'text-purple-700' },
  infrastructure:     { icon: MiniAlert,  bg: 'bg-gray-100',   text: 'text-gray-600' },
  stampede:           { icon: MiniUsers,  bg: 'bg-red-100',    text: 'text-red-700' },
  general:            { icon: MiniFile,   bg: 'bg-gray-100',   text: 'text-gray-600' },
}

function IncidentIcon({ type, size = "md" }) {
  const cfg = INCIDENT_CONFIG[type] || INCIDENT_CONFIG.general
  const Icon = cfg.icon
  const dim = size === "sm" ? "w-5 h-5" : "w-7 h-7"
  return (
    <div className={`${dim} rounded-lg ${cfg.bg} ${cfg.text} flex items-center justify-center shrink-0`}>
      <Icon />
    </div>
  )
}

const STATUS_OPTIONS = ['', 'filed', 'acknowledged', 'resolved', 'rejected']

async function downloadComplaintPDF(complaint) {
  const isGRPFIR = complaint.complaint_text?.includes('FIRST INFORMATION REPORT')
    || complaint.complaint_text?.includes('प्रथम सूचना रिपोर्ट')
    || complaint.complaint_text?.includes('प्रथम खबरी अहवाल')
  const isCPGRAMS = complaint.complaint_text?.includes('CPGRAMS')
  const isRCT = complaint.complaint_text?.includes('RAILWAY CLAIMS TRIBUNAL')
    || complaint.complaint_text?.includes('रेलवे दावा अधिकरण')

  let docTitle = 'Complaint Document'
  if (isGRPFIR) docTitle = 'First Information Report (FIR)'
  else if (isCPGRAMS) docTitle = 'CPGRAMS Grievance Form'
  else if (isRCT) docTitle = 'RCT Compensation Application'

  const bodyText = (complaint.complaint_text || 'No complaint text available')
    .replace(/[═╔╗╚╝╠╣╦╩╬║─┌┐└┘├┤┬┴┼]/g, '=')
    .replace(/[—–]/g, '-')
    .replace(/[^\x00-\x7F]/g, c => c.charCodeAt(0) > 255 ? '' : c)

  const doc = new jsPDF('p', 'pt', 'a4')
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 40
  const usable = pageWidth - margin * 2
  let y = margin

  // Title
  doc.setFontSize(16)
  doc.setFont('helvetica', 'bold')
  doc.text(docTitle, pageWidth / 2, y, { align: 'center' })
  y += 22

  // Separator line
  doc.setDrawColor(0)
  doc.setLineWidth(1.5)
  doc.line(margin, y, pageWidth - margin, y)
  y += 16

  // Reference & status
  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(100)
  doc.text(`Reference: ${complaint.ref} | Status: ${(complaint.status || '').toUpperCase()}`, pageWidth / 2, y, { align: 'center' })
  y += 18

  // Meta info
  doc.setTextColor(60)
  doc.text(`Complainant: ${complaint.user_name || 'N/A'}`, margin, y)
  doc.text(`Incident: ${(complaint.incident_type || '').replace('_', ' ').toUpperCase()}`, pageWidth / 2, y, { align: 'center' })
  doc.text(`Severity: ${(complaint.severity || '').toUpperCase()}`, pageWidth - margin, y, { align: 'right' })
  y += 20

  // Body text
  doc.setFontSize(10)
  doc.setTextColor(0)
  doc.setFont('courier', 'normal')
  const lines = doc.splitTextToSize(bodyText, usable)
  for (const line of lines) {
    if (y > pageHeight - margin) { doc.addPage(); y = margin }
    doc.text(line, margin, y)
    y += 14
  }

  // Footer
  y += 10
  if (y > pageHeight - margin) { doc.addPage(); y = margin }
  doc.setDrawColor(200)
  doc.setLineWidth(0.5)
  doc.line(margin, y, pageWidth - margin, y)
  y += 12
  doc.setFontSize(8)
  doc.setTextColor(150)
  doc.text(`Generated by Jan Suraksha Bot - RailFLOW Platform | ${new Date().toLocaleString('en-IN')}`, pageWidth / 2, y, { align: 'center' })

  // Save
  const filename = `${complaint.ref || 'complaint'}.pdf`
  try {
    if (Capacitor.isNativePlatform()) {
      const base64 = doc.output('datauristring').split(',')[1]
      const saved = await Filesystem.writeFile({ path: filename, data: base64, directory: Directory.Cache })
      await Share.share({ title: filename, url: saved.uri })
    } else {
      doc.save(filename)
    }
  } catch (err) {
    console.error('PDF save error:', err)
    alert('Failed to save PDF: ' + err.message)
  }
}

// ── Icons ──────────────────────────────────────────────
const IconRefresh   = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M1 4v6h6"/><path d="M23 20v-6h-6"/><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4-4.64 4.36A9 9 0 0 1 3.51 15"/></svg>
const IconMapPin    = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
const IconCpu       = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>
const IconBarChart  = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
const IconClipboard = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>
const IconFileDown  = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9 15 12 18 15 15"/></svg>

export default function PoliceDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [complaints, setComplaints] = useState([])
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [actionLoading, setActionLoading] = useState(null) // { ref, action }
  const [modal, setModal] = useState(null)
  const [toast, setToast] = useState(null)
  const [view, setView] = useState('tickets')
  const [analytics, setAnalytics] = useState(null)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)

  const fetchComplaints = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (statusFilter) params.set('status', statusFilter)
      if (typeFilter) params.set('type', typeFilter)
      const url = `/api/complaints/${params.toString() ? '?' + params.toString() : ''}`
      const res = await fetch(url)
      const data = await res.json()
      setComplaints(data.complaints || [])
    } catch {
      setComplaints([])
    } finally {
      setLoading(false)
    }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchComplaints() }, [statusFilter, typeFilter])

  const fetchAnalytics = async () => {
    setAnalyticsLoading(true)
    try {
      const res = await fetch('/api/safety/analytics')
      const data = await res.json()
      setAnalytics(data)
    } catch {
      setAnalytics(null)
    } finally {
      setAnalyticsLoading(false)
    }
  }

  useEffect(() => {
    if (view === 'analytics' && !analytics) fetchAnalytics()
  }, [view]) // eslint-disable-line react-hooks/exhaustive-deps

  const updateStatus = async (ref, status, note = '') => {
    setActionLoading({ ref, action: status })
    try {
      const res = await fetch(`/api/complaints/${ref}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, note }),
      })
      if (res.ok) {
        const label = status === 'acknowledged' ? 'Acknowledged' : status === 'resolved' ? 'Resolved' : 'Rejected'
        setToast(label)
        setTimeout(() => setToast(null), 2200)
        fetchComplaints()
        setModal(null)
      }
    } catch { /* noop */ } finally {
      setActionLoading(null)
    }
  }

  const openModal = (ref, action) => setModal({ ref, action, note: '' })

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // Stats
  const stats = {
    filed: complaints.filter(c => c.status === 'filed').length,
    acknowledged: complaints.filter(c => c.status === 'acknowledged').length,
    resolved: complaints.filter(c => c.status === 'resolved').length,
    rejected: complaints.filter(c => c.status === 'rejected').length,
  }

  return (
    <div className="min-h-screen bg-gray-50 max-w-sm mx-auto relative">

      {/* ── HEADER ── */}
      <div className="bg-gradient-to-br from-blue-700 via-blue-800 to-indigo-900 pt-10 pb-5 px-4 shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center">
                <span className="text-white font-black text-xs">m</span>
              </div>
              <span className="text-white font-black text-lg tracking-tight">Indicator</span>
              <span className="text-blue-300 text-xs font-semibold bg-blue-600/60 px-1.5 py-0.5 rounded">AI</span>
            </div>
            <p className="text-blue-300 text-[10px] mt-0.5">Mumbai Local · Powered by RailFlow</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-blue-200 text-[10px]">{user?.name}</span>
            <button onClick={handleLogout}
              className="text-[10px] bg-blue-600/60 hover:bg-blue-600 text-blue-200 px-2.5 py-1 rounded-lg transition-colors font-medium">
              Logout
            </button>
          </div>
        </div>

        <div className="pt-1">
          <p className="text-white font-bold text-base">Police Dashboard</p>
          <p className="text-blue-300 text-xs mt-0.5">Jan Suraksha Complaint Management</p>
        </div>

        {/* Stats row */}
        <div className="flex gap-2 mt-3">
          {[
            { key: 'filed',        label: 'Filed',  bg: 'bg-red-500/80' },
            { key: 'acknowledged', label: 'Active', bg: 'bg-amber-500/80' },
            { key: 'resolved',     label: 'Solved', bg: 'bg-emerald-500/80' },
            { key: 'rejected',     label: 'Closed', bg: 'bg-gray-400/80' },
          ].map(s => (
            <div key={s.key} className={`flex-1 ${s.bg} rounded-lg px-2 py-2 text-center`}>
              <div className="text-white text-lg font-black">{stats[s.key]}</div>
              <div className="text-white/80 text-[9px] font-semibold">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Tickets / Analytics toggle */}
        <div className="flex gap-2 mt-3">
          {[
            { id: 'tickets', label: 'Tickets' },
            { id: 'analytics', label: 'Analytics' },
          ].map(t => (
            <button key={t.id} onClick={() => setView(t.id)}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all active:scale-[0.97] ${
                view === t.id
                  ? 'bg-white text-blue-700 shadow-sm'
                  : 'bg-blue-600/60 text-blue-200 hover:bg-blue-600'
              }`}>
              <span className="inline-flex items-center gap-1.5">{t.id === 'analytics' ? <IconBarChart /> : <IconClipboard />}{t.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── ANALYTICS VIEW ── */}
      {view === 'analytics' && (
        <div className="px-3 pt-3 pb-6">
          {analyticsLoading && (
            <div className="text-center text-gray-400 py-12 text-xs">
              <span className="w-5 h-5 border-2 border-blue-600/30 border-t-blue-600 rounded-full animate-spin inline-block mb-2" />
              <p>Loading analytics...</p>
            </div>
          )}

          {!analyticsLoading && analytics && (
            <div className="space-y-3">
              {/* Stat cards */}
              <div className="flex gap-2">
                <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm p-3 text-center hover:shadow-md transition-shadow">
                  <div className="text-2xl font-black text-gray-900">{analytics.total_complaints}</div>
                  <div className="text-[10px] text-gray-500 font-semibold uppercase mt-0.5">Total</div>
                </div>
                <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm p-3 text-center hover:shadow-md transition-shadow">
                  <div className={`text-2xl font-black ${analytics.trend === 'up' ? 'text-red-600' : analytics.trend === 'down' ? 'text-emerald-600' : 'text-gray-600'}`}>
                    {analytics.trend === 'up' ? `+${analytics.this_week - analytics.last_week}` : analytics.trend === 'down' ? `${analytics.this_week - analytics.last_week}` : '0'}
                  </div>
                  <div className="text-[10px] text-gray-500 font-semibold uppercase mt-0.5">
                    {analytics.trend === 'up' ? 'This week' : analytics.trend === 'down' ? 'This week' : 'Stable'}
                  </div>
                </div>
                <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm p-3 text-center hover:shadow-md transition-shadow">
                  <div className="flex justify-center"><IncidentIcon type={analytics.by_type?.[0]?.incident_type} /></div>
                  <div className="text-[10px] text-gray-500 font-semibold uppercase mt-0.5">
                    {analytics.by_type?.[0]?.incident_type?.replace('_', ' ') || 'N/A'}
                  </div>
                </div>
              </div>

              {/* Complaints by Type — horizontal bar chart */}
              {analytics.by_type?.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
                  <p className="text-[11px] font-bold text-gray-500 uppercase tracking-widest mb-3">Complaints by Type</p>
                  <div className="space-y-2">
                    {analytics.by_type.map(item => {
                      const maxCount = analytics.by_type[0]?.count || 1
                      const pct = Math.round((item.count / maxCount) * 100)
                      return (
                        <div key={item.incident_type} className="flex items-center gap-2">
                          <IncidentIcon type={item.incident_type} size="sm" />
                          <span className="text-xs text-gray-600 font-medium w-20 truncate">{item.incident_type?.replace('_', ' ')}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                            <div className="bg-blue-500 h-full rounded-full transition-all" style={{ width: `${pct}%` }} />
                          </div>
                          <span className="text-xs font-bold text-gray-700 w-6 text-right">{item.count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Severity Breakdown */}
              {analytics.by_severity?.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
                  <p className="text-[11px] font-bold text-gray-500 uppercase tracking-widest mb-3">Severity Breakdown</p>
                  <div className="space-y-2">
                    {analytics.by_severity.map(item => {
                      const maxCount = Math.max(...analytics.by_severity.map(s => s.count), 1)
                      const pct = Math.round((item.count / maxCount) * 100)
                      const barColor = {
                        critical: 'bg-red-500', high: 'bg-orange-500',
                        medium: 'bg-amber-400', low: 'bg-blue-400',
                      }[item.severity] || 'bg-gray-400'
                      return (
                        <div key={item.severity} className="flex items-center gap-2">
                          <span className="text-xs text-gray-600 font-medium w-14 capitalize">{item.severity}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                            <div className={`${barColor} h-full rounded-full transition-all`} style={{ width: `${pct}%` }} />
                          </div>
                          <span className="text-xs font-bold text-gray-700 w-6 text-right">{item.count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Station Hotspots */}
              {analytics.by_station?.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
                  <p className="text-[11px] font-bold text-gray-500 uppercase tracking-widest mb-3">Station Hotspots</p>
                  <div className="space-y-2">
                    {analytics.by_station.slice(0, 6).map(item => {
                      const maxCount = analytics.by_station[0]?.count || 1
                      const pct = Math.round((item.count / maxCount) * 100)
                      return (
                        <div key={item.from_station} className="flex items-center gap-2">
                          <div className="w-5 h-5 rounded bg-rose-100 text-rose-600 flex items-center justify-center"><IconMapPin /></div>
                          <span className="text-xs text-gray-600 font-medium w-24 truncate">{item.from_station}</span>
                          <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
                            <div className="bg-rose-500 h-full rounded-full transition-all" style={{ width: `${pct}%` }} />
                          </div>
                          <span className="text-xs font-bold text-gray-700 w-6 text-right">{item.count}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Hourly Pattern */}
              {analytics.by_hour?.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md transition-shadow">
                  <p className="text-[11px] font-bold text-gray-500 uppercase tracking-widest mb-3">Hourly Pattern</p>
                  <div className="flex items-end gap-1 h-32">
                    {Array.from({ length: 24 }, (_, i) => {
                      const hourStr = String(i).padStart(2, '0')
                      const entry = analytics.by_hour.find(h => h.hour === hourStr)
                      const count = entry?.count || 0
                      const maxH = Math.max(...analytics.by_hour.map(h => h.count), 1)
                      const heightPct = count > 0 ? Math.max(10, Math.round((count / maxH) * 100)) : 0
                      const ampm = i === 0 ? '12a' : i < 12 ? `${i}a` : i === 12 ? '12p' : `${i-12}p`
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center justify-end h-full">
                          {count > 0 && (
                            <span className="text-[8px] text-gray-500 font-bold mb-0.5">{count}</span>
                          )}
                          <div
                            className={`w-full rounded-t transition-all ${count > 0 ? 'bg-blue-500' : 'bg-gray-100'}`}
                            style={{ height: count > 0 ? `${heightPct}%` : '4px' }}
                          />
                          {(i % 4 === 0) && (
                            <span className="text-[8px] text-gray-400 mt-1">{ampm}</span>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* AI Patrol Recommendation */}
              {analytics.patrol_recommendation && (
                <div className="bg-blue-50 rounded-xl border-2 border-blue-200 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-6 h-6 rounded-lg bg-blue-200 text-blue-700 flex items-center justify-center"><IconCpu /></div>
                    <span className="text-xs font-bold text-blue-700 uppercase tracking-wide">AI Patrol Recommendation</span>
                  </div>
                  <p className="text-sm text-blue-800 leading-relaxed">{analytics.patrol_recommendation}</p>
                </div>
              )}

              {/* Refresh */}
              <button onClick={fetchAnalytics}
                className="w-full py-2.5 bg-white border border-gray-200 rounded-xl text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
                <IconRefresh /> Refresh Analytics
              </button>
            </div>
          )}

          {!analyticsLoading && !analytics && (
            <div className="text-center text-gray-400 py-12 bg-white rounded-xl shadow-sm">
              <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center mx-auto mb-2 text-gray-400"><IconBarChart /></div>
              <p className="text-sm font-medium">Analytics unavailable</p>
              <p className="text-xs mt-1">File complaints via Jan Suraksha Bot to see data here</p>
            </div>
          )}
        </div>
      )}

      {/* ── FILTERS (tickets view) ── */}
      {view === 'tickets' && <div className="px-3 pt-3 pb-1">
        {/* Status filter chips */}
        <div className="flex gap-1.5 overflow-x-auto pb-2">
          {STATUS_OPTIONS.map(s => (
            <button key={s || 'all'} onClick={() => setStatusFilter(s)}
              className={`px-3 py-1.5 rounded-full text-[10px] font-bold whitespace-nowrap transition-all active:scale-95 ${
                statusFilter === s
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'bg-white text-gray-500 border border-gray-200'
              }`}>
              {s ? s.charAt(0).toUpperCase() + s.slice(1) : 'All'}
            </button>
          ))}
        </div>
        {/* Type + Refresh row */}
        <div className="flex gap-2 items-center">
          <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-xs bg-white text-gray-600">
            <option value="">All incident types</option>
            {Object.keys(INCIDENT_CONFIG).map(t => (
              <option key={t} value={t}>{t.replace('_', ' ')}</option>
            ))}
          </select>
          <button onClick={fetchComplaints}
            className="w-9 h-9 bg-blue-600 text-white rounded-lg flex items-center justify-center hover:bg-blue-700 transition-colors">
            <IconRefresh />
          </button>
        </div>
      </div>}

      {/* ── TICKETS ── */}
      {view === 'tickets' && <div className="px-3 pt-2 pb-6 space-y-2.5">
        {loading && (
          <div className="text-center text-gray-400 py-12 text-xs">
            <span className="w-5 h-5 border-2 border-blue-600/30 border-t-blue-600 rounded-full animate-spin inline-block mb-2" />
            <p>Loading complaints...</p>
          </div>
        )}

        {!loading && complaints.length === 0 && (
          <div className="text-center text-gray-400 py-12 bg-white rounded-xl shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center mx-auto mb-2 text-gray-400"><IconClipboard /></div>
            <p className="text-sm font-medium">No complaints found</p>
            <p className="text-xs mt-1">Tickets from Jan Suraksha Bot appear here</p>
          </div>
        )}

        {complaints.map(c => (
          <div key={c.ref} className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-200">
            {/* Header */}
            <div className="px-4 py-3">
              <div className="flex items-start gap-2.5">
                <IncidentIcon type={c.incident_type} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap mb-1">
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${STATUS_COLORS[c.status] || ''}`}>
                      {c.status?.toUpperCase()}
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${SEVERITY_COLORS[c.severity] || ''}`}>
                      {c.severity?.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-sm font-bold text-gray-900">
                    {c.incident_type?.replace('_', ' ').toUpperCase()}
                  </div>
                  <div className="text-[10px] text-gray-400 mt-0.5">
                    {c.user_name || 'Unknown'} · {c.authority || 'N/A'}
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className="font-mono text-[9px] text-gray-400">{c.ref}</div>
                  <div className="text-[9px] text-gray-400 mt-0.5">
                    {c.date_filed ? new Date(c.date_filed).toLocaleDateString('en-IN', {
                      day: '2-digit', month: 'short',
                    }) : ''}
                  </div>
                </div>
              </div>
            </div>

            {/* User Message */}
            <div className="px-4 pb-2">
              <div className="bg-gray-50 rounded-lg px-3 py-2 text-xs text-gray-600 italic leading-relaxed">
                "{c.user_message || 'No message'}"
              </div>
            </div>

            {/* Officer Note */}
            {c.officer_note && (
              <div className="px-4 pb-2">
                <div className="bg-blue-50 rounded-lg px-3 py-2 text-[10px] text-blue-700">
                  Officer: {c.officer_note}
                </div>
              </div>
            )}

            {/* Complaint Text + Download */}
            {c.complaint_text && (
              <div className="px-4 pb-2 space-y-1.5">
                <details className="bg-gray-50 rounded-lg border border-gray-200">
                  <summary className="px-3 py-2 text-[10px] font-semibold text-gray-500 cursor-pointer">
                    View Complaint Draft
                  </summary>
                  <div className="px-3 py-2 text-[10px] whitespace-pre-wrap border-t border-gray-100 bg-white max-h-48 overflow-y-auto font-mono leading-relaxed">
                    {c.complaint_text}
                  </div>
                </details>
                <button onClick={() => downloadComplaintPDF(c)}
                  className="w-full flex items-center justify-center gap-1.5 py-2 bg-blue-600 text-white rounded-lg text-[10px] font-semibold hover:bg-blue-700 transition-colors">
                  <IconFileDown /> Download FIR / Complaint PDF
                </button>
              </div>
            )}

            {/* Action Buttons — filed */}
            {c.status === 'filed' && (
              <div className="px-4 py-2.5 bg-gray-50 border-t border-gray-100 flex gap-2">
                <button onClick={() => updateStatus(c.ref, 'acknowledged')} disabled={actionLoading?.ref === c.ref}
                  className="flex-1 py-2 bg-amber-500 text-white rounded-lg text-[10px] font-bold hover:bg-amber-600 active:scale-[0.97] transition-all disabled:opacity-60">
                  {actionLoading?.ref === c.ref && actionLoading?.action === 'acknowledged'
                    ? <span className="flex items-center justify-center gap-1"><span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />Updating...</span>
                    : 'Acknowledge'}
                </button>
                <button onClick={() => openModal(c.ref, 'resolved')} disabled={actionLoading?.ref === c.ref}
                  className="flex-1 py-2 bg-emerald-600 text-white rounded-lg text-[10px] font-bold hover:bg-emerald-700 active:scale-[0.97] transition-all disabled:opacity-60">
                  Resolve
                </button>
                <button onClick={() => openModal(c.ref, 'rejected')} disabled={actionLoading?.ref === c.ref}
                  className="flex-1 py-2 bg-red-500 text-white rounded-lg text-[10px] font-bold hover:bg-red-600 active:scale-[0.97] transition-all disabled:opacity-60">
                  Reject
                </button>
              </div>
            )}

            {/* Action Buttons — acknowledged */}
            {c.status === 'acknowledged' && (
              <div className="px-4 py-2.5 bg-gray-50 border-t border-gray-100 flex gap-2">
                <button onClick={() => openModal(c.ref, 'resolved')} disabled={actionLoading?.ref === c.ref}
                  className="flex-1 py-2 bg-emerald-600 text-white rounded-lg text-[10px] font-bold hover:bg-emerald-700 active:scale-[0.97] transition-all disabled:opacity-60">
                  Resolve
                </button>
                <button onClick={() => openModal(c.ref, 'rejected')} disabled={actionLoading?.ref === c.ref}
                  className="flex-1 py-2 bg-red-500 text-white rounded-lg text-[10px] font-bold hover:bg-red-600 active:scale-[0.97] transition-all disabled:opacity-60">
                  Reject
                </button>
              </div>
            )}
          </div>
        ))}
      </div>}

      {/* ── MODAL ── */}
      {modal && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50">
          <div className="absolute inset-0" onClick={() => setModal(null)} />
          <div className="relative w-full max-w-sm mx-auto bg-white rounded-t-2xl shadow-2xl animate-slide-up">
            <div className="px-5 py-4 border-b border-gray-100">
              <div className="font-bold text-sm text-gray-900">
                {modal.action === 'resolved' ? 'Resolve Complaint' : 'Reject Complaint'}
              </div>
              <div className="text-[10px] text-gray-400 mt-0.5 font-mono">{modal.ref}</div>
            </div>

            <div className="px-5 py-4">
              <label className="block text-[10px] text-gray-500 font-semibold uppercase tracking-widest mb-2">
                {modal.action === 'resolved' ? 'Resolution note (optional)' : 'Reason for rejection (required)'}
              </label>
              <textarea
                value={modal.note}
                onChange={e => setModal({ ...modal, note: e.target.value })}
                rows={3}
                placeholder={modal.action === 'resolved'
                  ? 'e.g. Phone recovered from suspect at Dadar station'
                  : 'e.g. Insufficient evidence to proceed'}
                className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none"
                autoFocus
              />
            </div>

            <div className="px-5 py-3 bg-gray-50 rounded-b-2xl flex gap-2">
              <button onClick={() => setModal(null)} disabled={!!actionLoading}
                className="flex-1 py-2.5 text-sm text-gray-600 font-medium bg-white border border-gray-200 rounded-xl disabled:opacity-50">
                Cancel
              </button>
              <button
                onClick={() => {
                  if (modal.action === 'rejected' && !modal.note.trim()) return
                  updateStatus(modal.ref, modal.action, modal.note)
                }}
                disabled={(modal.action === 'rejected' && !modal.note.trim()) || !!actionLoading}
                className={`flex-1 py-2.5 rounded-xl text-sm font-bold text-white transition-all active:scale-[0.97] disabled:opacity-60 ${
                  modal.action === 'resolved'
                    ? 'bg-emerald-600 hover:bg-emerald-700'
                    : 'bg-red-500 hover:bg-red-600'
                }`}>
                {actionLoading?.ref === modal.ref
                  ? <span className="flex items-center justify-center gap-1.5"><span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />Updating...</span>
                  : modal.action === 'resolved' ? 'Resolve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success Toast */}
      {toast && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[60] animate-toast-in">
          <div className="flex items-center gap-2 bg-gray-900 text-white text-xs font-semibold px-4 py-2.5 rounded-full shadow-lg">
            <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5"/></svg>
            {toast}
          </div>
        </div>
      )}

      <style>{`
        @keyframes slide-up {
          from { transform: translateY(100%); }
          to { transform: translateY(0); }
        }
        .animate-slide-up { animation: slide-up 0.3s cubic-bezier(0.32, 0.72, 0, 1); }
        @keyframes toast-in {
          0% { opacity: 0; transform: translateY(-12px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .animate-toast-in { animation: toast-in 0.25s ease-out; }
      `}</style>
    </div>
  )
}