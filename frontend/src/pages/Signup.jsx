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
      // Send empty strings as null for optional fields
      if (!payload.phone) payload.phone = null
      if (!payload.address) payload.address = null
      const user = await signup(payload)
      navigate(user.role === 'police' ? '/police' : '/bot')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1e3a5f] to-[#0d1b2a] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">
            Rail<span className="text-[#ff6b35]">FLOW</span>
          </h1>
          <p className="text-blue-200 text-sm mt-1">Railway Passenger Safety Platform</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Create Account</h2>

          {error && (
            <div className="mb-4 bg-red-50 text-red-700 text-sm rounded-lg px-4 py-3 border border-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Role Toggle */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">I am a</label>
              <div className="flex gap-2">
                {[
                  { value: 'passenger', label: 'Passenger' },
                  { value: 'police', label: 'Police Officer' },
                ].map((r) => (
                  <button
                    key={r.value}
                    type="button"
                    onClick={() => setForm({ ...form, role: r.value })}
                    className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-colors border-2 ${
                      form.role === r.value
                        ? 'border-[#ff6b35] bg-orange-50 text-[#ff6b35]'
                        : 'border-gray-200 bg-white text-gray-500 hover:border-gray-300'
                    }`}
                  >
                    {r.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                value={form.name}
                onChange={set('name')}
                required
                className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[#ff6b35] focus:ring-1 focus:ring-[#ff6b35]"
                placeholder="Your full name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={form.email}
                onChange={set('email')}
                required
                className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[#ff6b35] focus:ring-1 focus:ring-[#ff6b35]"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                value={form.password}
                onChange={set('password')}
                required
                minLength={4}
                className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[#ff6b35] focus:ring-1 focus:ring-[#ff6b35]"
                placeholder="Choose a password"
              />
            </div>

            {/* Language preference */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Preferred Language</label>
              <div className="flex gap-2">
                {[
                  { code: 'en', label: 'English' },
                  { code: 'hi', label: 'Hindi' },
                  { code: 'mr', label: 'Marathi' },
                ].map((l) => (
                  <button
                    key={l.code}
                    type="button"
                    onClick={() => setForm({ ...form, language_pref: l.code })}
                    className={`flex-1 py-2 rounded-lg text-xs font-medium transition-colors ${
                      form.language_pref === l.code
                        ? 'bg-[#1e3a5f] text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {l.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Contact details — passengers only (used in FIR / complaint) */}
            {form.role === 'passenger' && (
              <div className="border-t border-gray-100 pt-4">
                <p className="text-xs text-gray-400 mb-3">Contact details (used in complaint / FIR filing)</p>
                <div className="space-y-3">
                  <div>
                    <input
                      type="tel"
                      value={form.phone}
                      onChange={set('phone')}
                      className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[#ff6b35] focus:ring-1 focus:ring-[#ff6b35]"
                      placeholder="Phone number (e.g. 9876543210)"
                    />
                  </div>
                  <div>
                    <input
                      type="text"
                      value={form.address}
                      onChange={set('address')}
                      className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-[#ff6b35] focus:ring-1 focus:ring-[#ff6b35]"
                      placeholder="Home address (for FIR / complaint)"
                    />
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#ff6b35] text-white py-3 rounded-xl font-semibold hover:bg-[#e55a2b] transition-colors disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="text-[#ff6b35] font-semibold hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}