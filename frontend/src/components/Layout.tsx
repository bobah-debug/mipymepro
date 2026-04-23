import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import {
  LayoutDashboard, Package, ShoppingCart, Monitor,
  Users, FileText, Building2, UserCog, LogOut, ChevronRight
} from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/inventory', icon: Package, label: 'Inventario' },
  { to: '/pos', icon: Monitor, label: 'Punto de Venta' },
  { to: '/sales', icon: ShoppingCart, label: 'Ventas' },
  { to: '/employees', icon: Users, label: 'RRHH' },
  { to: '/reports', icon: FileText, label: 'Reportes' },
  { to: '/company', icon: Building2, label: 'Empresa' },
  { to: '/users', icon: UserCog, label: 'Usuarios', adminOnly: true },
]

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const visibleItems = navItems.filter(
    (item) => !item.adminOnly || user?.role === 'admin'
  )

  return (
    <div className="flex h-screen bg-gray-50">
      <aside className="w-64 bg-gray-900 text-white flex flex-col shadow-xl">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-xl font-bold text-white">Mi PyME PRO</h1>
          <p className="text-gray-400 text-xs mt-1">Administración Empresarial</p>
        </div>

        <nav className="flex-1 py-4 overflow-y-auto">
          {visibleItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors duration-150 group',
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                )
              }
            >
              <item.icon size={18} />
              {item.label}
              <ChevronRight size={14} className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-bold">
              {user?.full_name?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-400 capitalize">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
          >
            <LogOut size={16} />
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
