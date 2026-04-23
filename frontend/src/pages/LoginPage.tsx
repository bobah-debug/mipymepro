import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import { toast } from 'sonner'
import { Building2 } from 'lucide-react'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { username, password })
      login(data.access_token, data.user)
      navigate('/dashboard')
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-primary-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
            <Building2 size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Mi PyME PRO</h1>
          <p className="text-gray-400 mt-2">Administración Empresarial Chile</p>
        </div>

        <form onSubmit={handleSubmit} className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Iniciar Sesión</h2>

          <div className="space-y-4">
            <div>
              <label className="label">Usuario o Email</label>
              <input
                type="text"
                className="input"
                placeholder="admin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
              />
            </div>
            <div>
              <label className="label">Contraseña</label>
              <input
                type="password"
                className="input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="btn-primary w-full mt-6" disabled={loading}>
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>

          <p className="text-xs text-gray-500 text-center mt-4">
            Usuario por defecto: <strong>admin</strong> / Contraseña: <strong>admin1234</strong>
          </p>
        </form>
      </div>
    </div>
  )
}
