import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Signup() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'passenger',
    language_pref: 'en',
    phone: '',
    address: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = { ...form }
      if (!payload.phone) payload.phone = null
      if (!payload.address) payload.address = null
      const user = await signup(payload)
      navigate(user.role === 'police' ? '/police' : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 max-w-sm mx-auto relative">
      {/* Header */}
      <div className="bg-gradient-to-b from-blue-700 to-blue-800 pt-14 pb-8 px-6 shadow-lg">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
            <span className="text-white font-black text-sm">m</span>
          </div>
          <span className="text-white font-black text-xl tracking-tight">Indicator</span>
          <span className="text-blue-300 text-xs font-semibold bg-blue-600/60 px-1.5 py-0.5 rounded">AI</span>
        </div>
        <p className="text-blue-300 text-xs">Mumbai Local · Powered by RailFlow</p>
        <p className="text-white font-bold text-lg mt-4">Create Account</p>
        <p className="text-blue-300 text-xs mt-0.5">Join to file complaints & find safe trains</p>
      </div>

      {/* Form */}
      <div className="px-5 -mt-2 pb-8">
        <div className="bg-white rounded-2xl shadow-lg p-6">
          {error && (
            <div className="mb-4 bg-red-50 text-red-700 text-xs rounded-lg px-3 py-2.5 border border-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            {/* Role Toggle */}
            <div>
              <label className="text-[10px] text-gray-500 font-semibold uppercase tracking-widest pl-1">I am a</label>
              <div className="flex gap-2 mt-1">
                {[
                  { value: 'passenger', label: 'Passenger' },
                  { value: 'police', label: 'Police Officer' },
                ].map((r) => (
                  <button
                    key={r.value}
                    type="button"
                    onClick={() => setForm({ ...form, role: r.value })}
                    className={`flex-1 py-2.5 rounded-xl text-xs font-semibold transition-colors border-2 ${
                      form.role === r.value
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 bg-white text-gray-400 hover:border-gray-300'
                    }`}
                  >
                    {r.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-[10px] text-gray-500 font-semibold uppercase tracking-widest pl-1">Full Name</label>
              <input
                type="text"
                value={form.name}
                onChange={set('name')}
                required
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm mt-1 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="Your full name"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 font-semibold uppercase tracking-widest pl-1">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={set('email')}
                required
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm mt-1 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 font-semibold uppercase tracking-widest pl-1">Password</label>
              <input
                type="password"
                value={form.password}
                onChange={set('password')}
                required
                minLength={4}
                className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm mt-1 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                placeholder="Choose a password"
              />
            </div>

            {/* Language */}
            <div>
              <label className="text-[10px] text-gray-500 font-semibold uppercase tracking-widest pl-1">Preferred Language</label>
              <div className="flex gap-1.5 mt-1">
                {[
                  { code: 'en', label: 'English' },
                  { code: 'hi', label: 'Hindi' },
                  { code: 'mr', label: 'Marathi' },
                ].map((l) => (
                  <button
                    key={l.code}
                    type="button"
                    onClick={() => setForm({ ...form, language_pref: l.code })}
                    className={`flex-1 py-2 rounded-lg text-xs font-semibold transition-colors ${
                      form.language_pref === l.code
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Contact — passengers only (required for FIR filing) */}
            {form.role === 'passenger' && (
              <div className="border-t border-gray-100 pt-3">
                <p className="text-[10px] text-gray-400 mb-2.5 pl-1">Contact details (required for complaint / FIR filing)</p>
                <div className="space-y-2.5">
                  <input
                    type="tel"
                    value={form.phone}
                    onChange={set('phone')}
                    required
                    className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    placeholder="Phone number (e.g. 9876543210)"
                  />
                  <input
                    type="text"
                    value={form.address}
                    onChange={set('address')}
                    required
                    className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                    placeholder="Home address (for FIR / complaint)"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold text-sm hover:bg-blue-700 transition-colors disabled:opacity-50 shadow-sm"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating account...
                </span>
              ) : 'Create Account'}
            </button>
          </form>

          <p className="mt-5 text-center text-xs text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 font-semibold hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
