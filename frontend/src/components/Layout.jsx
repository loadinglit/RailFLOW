import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const PASSENGER_NAV = [
  { to: '/bot', label: 'Jan Suraksha Bot', icon: '🛡️', desc: 'Legal Aid Chat' },
]

const POLICE_NAV = [
  { to: '/police', label: 'Police Dashboard', icon: '👮', desc: 'Complaint Tickets' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const navItems = user?.role === 'police' ? POLICE_NAV : PASSENGER_NAV

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-[#1e3a5f] text-white px-6 py-3 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-3">
          <div className="text-2xl font-bold tracking-tight">
            Rail<span className="text-[#ff6b35]">FLOW</span>
          </div>
          <span className="text-xs text-blue-200 hidden sm:block">
            Railway Passenger Safety Platform
          </span>
        </div>
        <div className="flex items-center gap-4">
          {user && (
            <>
              <div className="text-right hidden sm:block">
                <div className="text-sm font-medium">{user.name}</div>
                <div className="text-[10px] text-blue-300 capitalize">{user.role}</div>
              </div>
              <button
                onClick={handleLogout}
                className="text-xs bg-[#ff6b35] hover:bg-[#e55a2b] px-4 py-1.5 rounded-lg transition-colors font-medium"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </header>

      {/* Nav Tabs */}
      <nav className="bg-white border-b border-gray-200 px-4 flex gap-1 overflow-x-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                isActive
                  ? 'border-[#ff6b35] text-[#1e3a5f]'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`
            }
          >
            <span>{item.icon}</span>
            <div>
              <div className="font-semibold">{item.label}</div>
              <div className="text-[10px] text-gray-400">{item.desc}</div>
            </div>
          </NavLink>
        ))}
      </nav>

      {/* Main Content */}
      <main className="flex-1 p-4 max-w-7xl mx-auto w-full">
        <Outlet />
      </main>
    </div>
  )
}