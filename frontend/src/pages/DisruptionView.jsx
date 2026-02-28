import { useState } from 'react'

export default function DisruptionView() {
  const [disruption, setDisruption] = useState(null)
  const [cascade, setCascade] = useState([])
  const [reroute, setReroute] = useState(null)
  const [loading, setLoading] = useState(false)

  const [form, setForm] = useState({
    train_number: 'Virar Fast 08:05',
    line: 'WR',
    disruption_type: 'cancel',
    station: 'Dadar',
  })

  const [rerouteUserId, setRerouteUserId] = useState('rahul_001')

  const triggerDisruption = async (e) => {
    e.preventDefault()
    setLoading(true)
    setCascade([])
    setReroute(null)
    try {
      const res = await fetch('/api/disruption/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          detected_at: new Date().toISOString(),
        }),
      })
      const data = await res.json()
      setDisruption(data.disruption)
      setCascade(data.cascade || [])
    } catch { /* noop */ }
    finally { setLoading(false) }
  }

  const fetchCascade = async () => {
    try {
      const res = await fetch(`/api/disruption/cascade/${encodeURIComponent(form.train_number)}`)
      const data = await res.json()
      setCascade(data.cascade_risks || [])
    } catch { /* noop */ }
  }

  const fetchReroute = async () => {
    try {
      const res = await fetch(`/api/disruption/reroute/${rerouteUserId}`)
      const data = await res.json()
      setReroute(data.reroute || data)
    } catch { /* noop */ }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Trigger Panel */}
      <div className="bg-white rounded-xl shadow-sm p-5">
        <div className="font-semibold text-sm mb-4">Trigger Disruption (Demo)</div>
        <form onSubmit={triggerDisruption} className="space-y-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Train</label>
            <input
              type="text"
              value={form.train_number}
              onChange={e => setForm(prev => ({ ...prev, train_number: e.target.value }))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Line</label>
              <select
                value={form.line}
                onChange={e => setForm(prev => ({ ...prev, line: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
              >
                <option value="WR">Western</option>
                <option value="CR">Central</option>
                <option value="HR">Harbour</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Type</label>
              <select
                value={form.disruption_type}
                onChange={e => setForm(prev => ({ ...prev, disruption_type: e.target.value }))}
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
              >
                <option value="cancel">Cancellation</option>
                <option value="delay">Major Delay</option>
                <option value="megablock">Mega Block</option>
                <option value="signal_fail">Signal Failure</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Station</label>
            <input
              type="text"
              value={form.station}
              onChange={e => setForm(prev => ({ ...prev, station: e.target.value }))}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Trigger Disruption'}
          </button>
        </form>

        {/* Cascade button */}
        <button
          onClick={fetchCascade}
          className="w-full mt-3 bg-orange-500 text-white py-2 rounded-lg text-sm font-medium hover:bg-orange-600"
        >
          Fetch Cascade for {form.train_number}
        </button>
      </div>

      {/* Cascade Visualization */}
      <div className="bg-white rounded-xl shadow-sm p-5">
        <div className="font-semibold text-sm mb-4">Cascade Prediction</div>

        {disruption && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <div className="text-xs font-semibold text-red-800 mb-1">Disruption Active</div>
            <div className="text-xs text-red-700">
              <div>{disruption.train_number} — {disruption.disruption_type?.toUpperCase()}</div>
              <div>Station: {disruption.station || 'N/A'}</div>
              <div>Line: {disruption.line}</div>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {cascade.length === 0 && (
            <div className="text-center text-gray-400 py-8">
              <div className="text-3xl mb-2">⚡</div>
              <div className="text-sm">Trigger a disruption to see cascade effects</div>
            </div>
          )}
          {cascade.map((risk, i) => (
            <div key={i} className="bg-orange-50 border border-orange-200 rounded-lg p-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-semibold text-orange-900">{risk.affected_train}</span>
                <span className="text-xs font-bold text-orange-700">
                  {risk.predicted_surge_percent}% capacity
                </span>
              </div>
              <div className="w-full bg-orange-200 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full transition-all"
                  style={{ width: `${Math.min(risk.predicted_surge_percent, 200) / 2}%` }}
                />
              </div>
              <div className="text-[10px] text-orange-600 mt-1">
                Confidence: {(risk.confidence * 100).toFixed(0)}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Reroute Card */}
      <div className="bg-white rounded-xl shadow-sm p-5">
        <div className="font-semibold text-sm mb-4">Reroute Card</div>
        <div className="flex gap-2 mb-4">
          <select
            value={rerouteUserId}
            onChange={e => setRerouteUserId(e.target.value)}
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm"
          >
            <option value="rahul_001">Rahul (Virar→Churchgate)</option>
            <option value="priya_002">Priya (Thane→CST)</option>
            <option value="meena_003">Meena (Dadar→Churchgate)</option>
            <option value="arjun_004">Arjun (Bandra→Andheri)</option>
          </select>
          <button
            onClick={fetchReroute}
            className="bg-[#1e3a5f] text-white px-4 py-2 rounded-lg text-sm hover:bg-[#2a4f7f]"
          >
            Get
          </button>
        </div>

        {reroute ? (
          <div className="space-y-3">
            {reroute.options?.length > 0 ? (
              reroute.options.map((opt, i) => (
                <div key={i} className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="font-semibold text-sm text-green-900">{opt.train || 'Alternative'}</div>
                  <div className="text-xs text-green-700 mt-1">
                    {opt.platform && <span>Platform {opt.platform} | </span>}
                    {opt.crowd_score != null && <span>Crowd: {opt.crowd_score}/100 | </span>}
                    {opt.time_diff && <span>{opt.time_diff}</span>}
                  </div>
                  {opt.notes && <div className="text-[10px] text-green-600 mt-1">{opt.notes}</div>}
                </div>
              ))
            ) : (
              <div className="text-center text-gray-400 py-4 text-sm">
                {reroute.user_id ? 'No reroute options available' : 'Select a user and click Get'}
              </div>
            )}
            {reroute.multimodal_option && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="text-xs font-semibold text-blue-800">Multimodal Alternative</div>
                <div className="text-sm text-blue-700">{reroute.multimodal_option}</div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <div className="text-3xl mb-2">🗺️</div>
            <div className="text-sm">Select a user to see personalized reroute options</div>
          </div>
        )}
      </div>
    </div>
  )
}
