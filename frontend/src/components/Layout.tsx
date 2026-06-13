import { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import authService from '../services/authService'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate()

  const handleLogout = () => {
    authService.logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-2xl font-bold">Mini-ERP</h1>
          <p className="text-gray-400 text-sm">Comercial CNA</p>
        </div>

        <nav className="flex-1 p-6 space-y-2">
          <Link to="/tablero" className="block px-4 py-2 rounded-lg hover:bg-gray-800 transition">
            📊 Tablero
          </Link>
          <Link to="/clientes" className="block px-4 py-2 rounded-lg hover:bg-gray-800 transition">
            👥 Clientes
          </Link>
          <Link to="/productos" className="block px-4 py-2 rounded-lg hover:bg-gray-800 transition">
            📦 Productos
          </Link>
          <Link to="/ventas" className="block px-4 py-2 rounded-lg hover:bg-gray-800 transition">
            🛒 Ventas
          </Link>
          <Link to="/cobranza" className="block px-4 py-2 rounded-lg hover:bg-gray-800 transition">
            💰 Cobranza
          </Link>
        </nav>

        <div className="p-6 border-t border-gray-800">
          <button
            onClick={handleLogout}
            className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition"
          >
            Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  )
}
