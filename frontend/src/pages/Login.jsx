import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, password)
      navigate(user.role === 'police' ? '/police' : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 max-w-sm mx-auto relative">
      {/* Header — matches PassengerHome */}
      <div className="bg-gradient-to-br from-blue-700 via-blue-800 to-indigo-900 pt-14 pb-8 px-6 shadow-lg">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
            <span className="text-white font-black text-sm">m</span>
          </div>
          <span className="text-white font-black text-xl tracking-tight">Indicator</span>
          <span className="text-blue-300 text-xs font-semibold bg-blue-600/60 px-1.5 py-0.5 rounded">AI</span>
        </div>
        <p className="text-blue-300 text-xs">Mumbai Local · Powered by RailFlow</p>
        <p className="text-white font-bold text-lg mt-4">Welcome back</p>
        <p className="text-blue-300 text-xs mt-0.5">Sign in to continue</p>
      </div>

      {/* Form */}
      <div className="px-5 -mt-2">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
          {error && (
            <div className="mb-4 bg-red-50 text-red-700 text-xs rounded-lg px-3 py-2.5 border border-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[10px] text-gray-500 font-semibold uppercase tracking-widest pl-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm mt-1 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:bg-white transition-colors"
                placeholder="your@email.com"
              />
            </div>

            <div>
              <label className="text-[10px] text-gray-500 font-semibold uppercase tracking-widest pl-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm mt-1 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:bg-white transition-colors"
                placeholder="Enter password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-xl font-bold text-sm hover:from-blue-700 hover:to-indigo-700 hover:shadow-lg active:scale-[0.97] transition-all disabled:opacity-50 shadow-md"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Signing in...
                </span>
              ) : 'Sign In'}
            </button>
          </form>

          <p className="mt-5 text-center text-xs text-gray-400">
            Don't have an account?{' '}
            <Link to="/signup" className="text-blue-600 font-semibold hover:underline">
              Sign Up
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
