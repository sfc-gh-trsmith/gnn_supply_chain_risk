import { Outlet, NavLink } from 'react-router-dom'
import { 
  Home, BarChart3, Network, Target, Zap, Shield, 
  ChevronLeft, ChevronRight, MessageSquare 
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '../lib/utils'
import { CortexConversation } from './chat/CortexConversation'

const navItems = [
  { to: '/', icon: Home, label: 'Overview' },
  { to: '/executive', icon: BarChart3, label: 'Executive' },
  { to: '/network', icon: Network, label: 'Network' },
  { to: '/tier2', icon: Target, label: 'Tier-2 Analysis' },
  { to: '/simulator', icon: Zap, label: 'Simulator' },
  { to: '/mitigation', icon: Shield, label: 'Mitigation' },
]

export function Layout() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-slate-900 flex">
      <aside className={cn(
        'bg-slate-800 border-r border-slate-700 flex flex-col transition-all duration-200',
        collapsed ? 'w-16' : 'w-56'
      )}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          {!collapsed && (
            <div>
              <h1 className="font-bold text-sky-400 text-lg">Supply Chain</h1>
              <p className="text-xs text-slate-500">GNN Risk Analytics</p>
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 hover:bg-slate-700 rounded text-slate-400"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        <nav className="flex-1 p-2 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                isActive 
                  ? 'bg-sky-600/20 text-sky-400 border border-sky-600/30' 
                  : 'text-slate-400 hover:bg-slate-700 hover:text-slate-200'
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="text-sm">{label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-700">
          {!collapsed && (
            <div className="text-xs text-slate-500">
              Powered by Snowflake Cortex
            </div>
          )}
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>

      <CortexConversation />
    </div>
  )
}
