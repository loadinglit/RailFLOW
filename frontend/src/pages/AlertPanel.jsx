import { useState } from 'react'

const DEMO_USERS = [
  { id: 'rahul_001', name: 'Rahul', route: 'Virar → Churchgate (WR)' },
  { id: 'priya_002', name: 'Priya', route: 'Thane → CST (CR)' },
  { id: 'meena_003', name: 'Meena', route: 'Dadar → Churchgate (WR)' },
  { id: 'arjun_004', name: 'Arjun', route: 'Bandra → Andheri (WR)' },
]

function CrowdScoreGauge({ score }) {
  const color = score >= 80 ? '#e74c3c' : score >= 60 ? '#f39c12' : score >= 40 ? '#f1c40f' : '#2ecc71'
  const rotation = (score / 100) * 180 - 90

  return (
    <div className="relative w-32 h-16 mx-auto">
      {/* Background arc */}
      <svg viewBox="0 0 100 50" className="w-full h-full">
        <path d="M 5 50 A 45 45 0 0 1 95 50" fill="none" stroke="#e5e7eb" strokeWidth="8" strokeLinecap="round" />
        <path
          d="M 5 50 A 45 45 0 0 1 95 50"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${(score / 100) * 141.3} 141.3`}
        />
      </svg>
      <div className="absolute inset-0 flex items-end justify-center pb-0">
        <span className="text-2xl font-bold" style={{ color }}>{score}</span>
      </div>
    </div>
  )
}

export default function AlertPanel() {
  const [selectedUser, setSelectedUser] = useState('rahul_001')
  const [routine, setRoutine] = useState(null)
  const [alert, setAlert] = useState(null)
  const [triggerResult, setTriggerResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchRoutine = async (uid) => {
    try {
      const res = await fetch(`/api/guard/user/${uid}/routine`)
      const data = await res.json()
      setRoutine(data.routine || data)
    } catch { setRoutine(null) }
  }

  const fetchAlert = async (uid) => {
    setLoading(true)
    try {
      const res = await fetch(`/api/guard/user/${uid}/alert`)
      const data = await res.json()
      setAlert(data.alert || data)
    } catch { setAlert(null) }
    finally { setLoading(false) }
  }

  const triggerAll = async () => {
    try {
      const res = await fetch('/api/guard/trigger-all', { method: 'POST' })
      const data = await res.json()
      setTriggerResult(data)
    } catch { setTriggerResult({ error: true }) }
  }

  const handleUserChange = (uid) => {
    setSelectedUser(uid)
    setAlert(null)
    setRoutine(null)
    fetchRoutine(uid)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* User Selection */}
      <div className="bg-white rounded-xl shadow-sm p-5">
        <div className="font-semibold text-sm mb-4">Demo Users</div>
        <div className="space-y-2">
          {DEMO_USERS.map(u => (
            <button
              key={u.id}
              onClick={() => handleUserChange(u.id)}
              className={`w-full text-left p-3 rounded-lg border transition-colors ${
                selectedUser === u.id
                  ? 'border-[#ff6b35] bg-orange-50'
                  : 'border-gray-100 hover:border-gray-300 bg-gray-50'
              }`}
            >
              <div className="font-semibold text-sm">{u.name}</div>
              <div className="text-xs text-gray-500">{u.route}</div>
            </button>
          ))}
        </div>

        <button
          onClick={triggerAll}
          className="w-full mt-4 bg-[#1e3a5f] text-white py-2.5 rounded-lg text-sm font-medium hover:bg-[#2a4f7f]"
        >
          Trigger All Alerts (FCM Mock)
        </button>

        {triggerResult && (
          <div className="mt-3 bg-blue-50 rounded-lg p-3 text-xs text-blue-700">
            Triggered: {triggerResult.triggered ?? 0} alerts
            {triggerResult.message && <div className="text-gray-500 mt-1">{triggerResult.message}</div>}
          </div>
        )}
      </div>

      {/* Routine */}
      <div className="bg-white rounded-xl shadow-sm p-5">
        <div className="font-semibold text-sm mb-4">Commute Routine</div>
        {routine ? (
          <div className="space-y-3">
            {routine.user_id && (
              <>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div><span className="text-gray-500">Origin:</span> <span className="font-medium">{routine.origin}</span></div>
                    <div><span className="text-gray-500">Dest:</span> <span className="font-medium">{routine.destination}</span></div>
                    <div><span className="text-gray-500">Train:</span> <span className="font-medium">{routine.usual_train}</span></div>
                    <div><span className="text-gray-500">Line:</span> <span className="font-medium">{routine.line}</span></div>
                    <div><span className="text-gray-500">Departs:</span> <span className="font-medium">{routine.usual_departure}</span></div>
                    <div><span className="text-gray-500">Flex:</span> <span className="font-medium">{routine.flexibility_score}</span></div>
                  </div>
                </div>
              </>
            )}
            {!routine.user_id && (
              <div className="text-center text-gray-400 text-sm py-4">No routine data found</div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <div className="text-3xl mb-2">📋</div>
            <div className="text-sm">Select a user to see their routine</div>
          </div>
        )}

        <button
          onClick={() => fetchAlert(selectedUser)}
          disabled={loading}
          className="w-full mt-4 bg-[#ff6b35] text-white py-2.5 rounded-lg text-sm font-medium hover:bg-[#e55a2b] disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Alert'}
        </button>
      </div>

      {/* Alert Display */}
      <div className="bg-white rounded-xl shadow-sm p-5">
        <div className="font-semibold text-sm mb-4">Proactive Alert</div>

        {alert ? (
          <div className="space-y-4">
            {alert.crowd_score != null && (
              <div>
                <div className="text-xs text-center text-gray-500 mb-1">Crowd Score</div>
                <CrowdScoreGauge score={alert.crowd_score} />
              </div>
            )}

            {alert.title && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="font-semibold text-sm text-orange-900 mb-1">{alert.title}</div>
                <div className="text-xs text-orange-800">{alert.body}</div>
              </div>
            )}

            {alert.best_option && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="text-xs font-semibold text-green-800 mb-1">Best Option</div>
                <div className="text-sm text-green-700">{alert.best_option}</div>
              </div>
            )}

            {alert.alternative && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="text-xs font-semibold text-blue-800 mb-1">Alternative</div>
                <div className="text-sm text-blue-700">{alert.alternative}</div>
              </div>
            )}

            {alert.reasons?.length > 0 && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs font-semibold text-gray-600 mb-1">Reasons</div>
                <ul className="text-xs text-gray-700 space-y-1">
                  {alert.reasons.map((r, i) => (
                    <li key={i} className="flex items-start gap-1">
                      <span className="text-gray-400">•</span> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <div className="text-3xl mb-2">🔔</div>
            <div className="text-sm">Click "Generate Alert" to see today's proactive alert</div>
          </div>
        )}
      </div>
    </div>
  )
}
