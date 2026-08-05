import { NavLink, Outlet } from 'react-router-dom'
import clsx from 'clsx'
import {
  LayoutDashboard, Target, TrendingUp, Flag, Clock, Download
} from 'lucide-react'
import { exportApi } from '../api'

const nav = [
  { to: '/', label: 'Dashboard',    icon: LayoutDashboard, end: true },
  { to: '/objectives', label: 'Objetivos',    icon: Target },
  { to: '/indicators', label: 'Indicadores',  icon: TrendingUp },
  { to: '/milestones', label: 'Hitos',        icon: Flag },
  { to: '/snapshots',  label: 'Versiones',    icon: Clock },
]

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Sidebar */}
      <aside className="w-56 flex-shrink-0 bg-white border-r border-slate-100 flex flex-col">
        {/* Logo */}
        <div className="px-5 pt-6 pb-5">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shrink-0">
              <span className="text-white font-black text-xs">FP</span>
            </div>
            <div>
              <div className="font-bold text-slate-900 text-sm leading-tight">FONPLATA</div>
              <div className="text-xs text-slate-400">Plan Anual 2026</div>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="mx-4 border-t border-slate-100 mb-3" />

        {/* Nav */}
        <nav className="flex-1 px-3 space-y-0.5">
          {nav.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150',
                  isActive
                    ? 'bg-indigo-50 text-indigo-700 font-semibold'
                    : 'text-slate-500 hover:bg-slate-50 hover:text-slate-800'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon size={17} className={isActive ? 'text-indigo-600' : 'text-slate-400'} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-3 pb-5 space-y-1">
          <button
            onClick={exportApi.excel}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-800 transition-all w-full"
          >
            <Download size={17} className="text-slate-400" />
            Exportar Excel
          </button>
          <div className="px-3 pt-1 text-xs text-slate-300">v1.0 · 2026</div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        <Outlet />
      </main>
    </div>
  )
}
