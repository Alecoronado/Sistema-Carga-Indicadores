import { NavLink, Outlet } from 'react-router-dom'
import clsx from 'clsx'
import { LayoutDashboard, PlusCircle, RefreshCw, Calendar, Clock, Download, Target } from 'lucide-react'
import { exportApi } from '../api'

const nav = [
  { to: '/',           label: 'Dashboard',            icon: LayoutDashboard, end: true },
  { to: '/objetivos',  label: 'Objetivos',             icon: Target },
  { to: '/nuevo',      label: 'Nuevo Indicador',       icon: PlusCircle },
  { to: '/actualizar', label: 'Actualizar Indicador',  icon: RefreshCw },
  { to: '/gantt',      label: 'Gantt',                 icon: Calendar },
  { to: '/historial',  label: 'Historial',             icon: Clock },
]

export default function TopNav() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Top navbar */}
      <header className="bg-slate-700 text-white shadow-lg shrink-0">
        <div className="max-w-screen-2xl mx-auto px-6 flex items-center h-14 gap-6">
          {/* Logo */}
          <div className="flex items-center gap-3 mr-4">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center shrink-0">
              <span className="font-black text-xs text-white">FP</span>
            </div>
            <span className="font-bold text-sm whitespace-nowrap">Sistema de Indicadores</span>
          </div>

          {/* Nav links */}
          <nav className="flex items-center gap-1 flex-1">
            {nav.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150 whitespace-nowrap',
                    isActive
                      ? 'bg-slate-900/60 text-white'
                      : 'text-slate-300 hover:bg-slate-600 hover:text-white'
                  )
                }
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
          </nav>

          {/* Right side */}
          <button
            onClick={exportApi.excel}
            className="flex items-center gap-2 text-slate-300 hover:text-white hover:bg-slate-600 px-3 py-2 rounded-lg text-sm transition-all"
          >
            <Download size={15} />
            <span className="hidden lg:inline">Exportar Excel</span>
          </button>

          <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
            AC
          </div>
        </div>
      </header>

      {/* Page content */}
      <main className="flex-1 overflow-y-auto scrollbar-thin">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-slate-700 text-slate-400 text-xs text-center py-2.5 shrink-0">
        Sistema de Indicadores FONPLATA © 2026
      </footer>
    </div>
  )
}
