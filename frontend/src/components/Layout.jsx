import { NavLink, Outlet } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/bot', label: 'Jan Suraksha Bot', icon: '🛡️', desc: 'Legal Aid Chat' },
  { to: '/crowd', label: 'CrowdSignal', icon: '👥', desc: 'Live Crowd Feed' },
  { to: '/disruption', label: 'DisruptionBrain', icon: '⚡', desc: 'Cascade & Reroute' },
  { to: '/alerts', label: 'PersonalGuard', icon: '🔔', desc: 'Proactive Alerts' },
]

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-[#1e3a5f] text-white px-6 py-3 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-3">
          <div className="text-2xl font-bold tracking-tight">
            Rail<span className="text-[#ff6b35]">Mind</span>
          </div>
          <span className="text-xs text-blue-200 hidden sm:block">
            AI Intelligence Layer for Mumbai Suburban Railways
          </span>
        </div>
        <div className="text-xs text-blue-300">
          mIndicator AI Hackathon 2026
        </div>
      </header>

      {/* Nav Tabs */}
      <nav className="bg-white border-b border-gray-200 px-4 flex gap-1 overflow-x-auto">
        {NAV_ITEMS.map((item) => (
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
