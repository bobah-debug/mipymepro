import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { toast } from 'sonner'
import api from '../services/api'
import { User } from '../types'

function UserForm({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '', role_name: 'vendedor' })

  const mutation = useMutation({
    mutationFn: () => api.post('/auth/users', form),
    onSuccess: () => { toast.success('Usuario creado'); qc.invalidateQueries({ queryKey: ['users'] }); onClose() },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error'),
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold mb-4">Nuevo Usuario</h2>
        <div className="space-y-3">
          <div>
            <label className="label">Nombre Completo</label>
            <input className="input" value={form.full_name} onChange={e => setForm(f => ({...f, full_name: e.target.value}))} required />
          </div>
          <div>
            <label className="label">Usuario</label>
            <input className="input" value={form.username} onChange={e => setForm(f => ({...f, username: e.target.value}))} required />
          </div>
          <div>
            <label className="label">Email</label>
            <input type="email" className="input" value={form.email} onChange={e => setForm(f => ({...f, email: e.target.value}))} required />
          </div>
          <div>
            <label className="label">Contraseña</label>
            <input type="password" className="input" value={form.password} onChange={e => setForm(f => ({...f, password: e.target.value}))} required />
          </div>
          <div>
            <label className="label">Rol</label>
            <select className="input" value={form.role_name} onChange={e => setForm(f => ({...f, role_name: e.target.value}))}>
              <option value="admin">Administrador</option>
              <option value="vendedor">Vendedor</option>
              <option value="rrhh">RRHH</option>
              <option value="contador">Contador</option>
            </select>
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button className="btn-primary flex-1" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            Crear Usuario
          </button>
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  )
}

export default function UsersPage() {
  const [showForm, setShowForm] = useState(false)
  const { data: users } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: () => api.get('/auth/users').then(r => r.data),
  })

  const roleColors: Record<string, string> = {
    admin: 'badge-red',
    vendedor: 'badge-blue',
    rrhh: 'badge-green',
    contador: 'badge-yellow',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Usuarios del Sistema</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          <Plus size={16} /> Nuevo Usuario
        </button>
      </div>

      <div className="card overflow-hidden p-0">
        <table className="w-full text-sm">
          <thead className="table-header">
            <tr>
              <th className="px-4 py-3 text-left">Nombre</th>
              <th className="px-4 py-3 text-left">Usuario</th>
              <th className="px-4 py-3 text-left">Email</th>
              <th className="px-4 py-3 text-center">Rol</th>
              <th className="px-4 py-3 text-center">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {users?.map(u => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{u.full_name}</td>
                <td className="px-4 py-3 text-gray-600 font-mono text-xs">{u.username}</td>
                <td className="px-4 py-3 text-gray-600">{u.email}</td>
                <td className="px-4 py-3 text-center">
                  <span className={roleColors[u.role] || 'badge-gray'}>{u.role}</span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={u.is_active ? 'badge-green' : 'badge-gray'}>
                    {u.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && <UserForm onClose={() => setShowForm(false)} />}
    </div>
  )
}
