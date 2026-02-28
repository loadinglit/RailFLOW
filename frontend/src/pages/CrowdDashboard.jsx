import { useState, useEffect } from 'react'

const SEVERITY_COLORS = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  danger: 'bg-red-100 text-red-800',
}

const SIGNAL_ICONS = {
  crowd: '👥',
  delay: '🕐',
  cancel: '❌',
  fight: '⚠️',
  platform_change: '🔄',
  signal_fail: '🚦',
}

export default function CrowdDashboard() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(false)
  const [lineFilter, setLineFilter] = useState('')
  const [trainScore, setTrainScore] = useState(null)
  const [trainIdInput, setTrainIdInput] = useState('')

  // Manual ingest form
  const [ingestForm, setIngestForm] = useState({
    raw_text: '',
    signal_type: 'crowd',
    severity: 'medium',
    station: '',
    train_number: '',
    line: 'WR',
  })

  const fetchSignals = async () => {
    setLoading(true)
    try {
      const url = lineFilter ? `/api/crowdsignal/latest?line=${lineFilter}` : '/api/crowdsignal/latest'
      const res = await fetch(url)
      const data = await res.json()
      setSignals(data.signals || [])
    } catch {
      setSignals([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchSignals() }, [lineFilter])

  const fetchScore = async () => {
    if (!trainIdInput.trim()) return
    try {
      const res = await fetch(`/api/crowdsignal/score/${encodeURIComponent(trainIdInput)}`)
      const data = await res.json()
      setTrainScore(data)
    } catch {
      setTrainScore({ error: true })
    }
  }

  const ingestSignal = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch('/api/crowdsignal/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...ingestForm,
          timestamp: new Date().toISOString(),
          source: 'demo_ui',
        }),
      })
      if (res.ok) {
        setIngestForm(prev => ({ ...prev, raw_text: '', station: '', train_number: '' }))
        fetchSignals()
      }
    } catch { /* noop */ }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Left: Signal Feed */}
      <div className="lg:col-span-2 bg-white rounded-xl shadow-sm">
        <div className="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
          <div>
            <div className="font-semibold text-sm">Live Crowd Signals</div>
            <div className="text-[10px] text-gray-400">Engine 1 — NLP-parsed from chat messages</div>
          </div>
          <div className="flex gap-1">
            {['', 'WR', 'CR', 'HR'].map(line => (
              <button
                key={line}
                onClick={() => setLineFilter(line)}
                className={`px-3 py-1 rounded-lg text-xs font-medium ${
                  lineFilter === line
                    ? 'bg-[#1e3a5f] text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {line || 'All'}
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 space-y-3 max-h-[60vh] overflow-y-auto">
          {loading && <div className="text-center text-gray-400 py-8 text-sm">Loading...</div>}

          {!loading && signals.length === 0 && (
            <div className="text-center text-gray-400 py-12">
              <div className="text-3xl mb-2">👥</div>
              <div className="text-sm font-medium">No signals yet</div>
              <div className="text-xs mt-1">Use the ingest form to submit a crowd signal</div>
            </div>
          )}

          {signals.map((sig, i) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
              <div className="text-xl">{SIGNAL_ICONS[sig.signal_type] || '📡'}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${SEVERITY_COLORS[sig.severity] || ''}`}>
                    {sig.severity?.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-500">{sig.signal_type}</span>
                  {sig.station && <span className="text-xs text-gray-500">@ {sig.station}</span>}
                  {sig.train_number && <span className="text-xs text-blue-600">{sig.train_number}</span>}
                </div>
                <div className="text-sm text-gray-700">{sig.raw_text}</div>
                <div className="text-[10px] text-gray-400 mt-1">
                  {sig.timestamp ? new Date(sig.timestamp).toLocaleTimeString() : ''}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Controls */}
      <div className="space-y-4">
        {/* Crowd Score Lookup */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="font-semibold text-sm mb-3">Crowd Score Lookup</div>
          <div className="flex gap-2">
            <input
              type="text"
              value={trainIdInput}
              onChange={e => setTrainIdInput(e.target.value)}
              placeholder="Train name/number..."
              className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#ff6b35]"
            />
            <button
              onClick={fetchScore}
              className="bg-[#1e3a5f] text-white px-3 py-2 rounded-lg text-sm hover:bg-[#2a4f7f]"
            >
              Check
            </button>
          </div>
          {trainScore && (
            <div className="mt-3 bg-gray-50 rounded-lg p-3">
              <div className="text-2xl font-bold text-[#1e3a5f]">{trainScore.score ?? '—'}</div>
              <div className="text-xs text-gray-500">/ 100 crowd score</div>
            </div>
          )}
        </div>

        {/* Manual Ingest */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="font-semibold text-sm mb-3">Submit Signal (Demo)</div>
          <form onSubmit={ingestSignal} className="space-y-3">
            <textarea
              value={ingestForm.raw_text}
              onChange={e => setIngestForm(prev => ({ ...prev, raw_text: e.target.value }))}
              placeholder="Chat message text..."
              rows={2}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#ff6b35]"
              required
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                type="text"
                value={ingestForm.station}
                onChange={e => setIngestForm(prev => ({ ...prev, station: e.target.value }))}
                placeholder="Station"
                className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
              />
              <input
                type="text"
                value={ingestForm.train_number}
                onChange={e => setIngestForm(prev => ({ ...prev, train_number: e.target.value }))}
                placeholder="Train #"
                className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <select
                value={ingestForm.signal_type}
                onChange={e => setIngestForm(prev => ({ ...prev, signal_type: e.target.value }))}
                className="border border-gray-200 rounded-lg px-2 py-2 text-xs"
              >
                <option value="crowd">Crowd</option>
                <option value="delay">Delay</option>
                <option value="cancel">Cancel</option>
                <option value="fight">Fight</option>
                <option value="signal_fail">Signal Fail</option>
              </select>
              <select
                value={ingestForm.severity}
                onChange={e => setIngestForm(prev => ({ ...prev, severity: e.target.value }))}
                className="border border-gray-200 rounded-lg px-2 py-2 text-xs"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="danger">Danger</option>
              </select>
              <select
                value={ingestForm.line}
                onChange={e => setIngestForm(prev => ({ ...prev, line: e.target.value }))}
                className="border border-gray-200 rounded-lg px-2 py-2 text-xs"
              >
                <option value="WR">WR</option>
                <option value="CR">CR</option>
                <option value="HR">HR</option>
              </select>
            </div>
            <button
              type="submit"
              className="w-full bg-[#ff6b35] text-white py-2 rounded-lg text-sm font-medium hover:bg-[#e55a2b]"
            >
              Submit Signal
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
