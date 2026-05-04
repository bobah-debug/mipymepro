import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, X } from 'lucide-react'
import { toast } from 'sonner'
import api from '../services/api'
import { User } from '../types'

const ROLES = [
  { value: 'admin',    label: 'Administrador' },
  { value: 'vendedor', label: 'Vendedor' },
  { value: 'rrhh',     label: 'RRHH' },
  { value: 'contador', label: 'Contador' },
]

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
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold">Nuevo Usuario</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
        </div>
        <div className="p-6 space-y-3">
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
              {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>
        </div>
        <div className="flex gap-2 px-6 pb-6">
          <button className="btn-primary flex-1" onClick={() => mutation.mutate()}
            disabled={!form.username || !form.email || !form.full_name || !form.password || mutation.isPending}>
            {mutation.isPending ? 'Creando...' : 'Crear Usuario'}
          </button>
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  )
}

function EditUserModal({ user, onClose }: { user: User; onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    full_name: user.full_name,
    email: user.email,
    role_name: user.role,
    password: '',
    is_active: user.is_active,
  })

  const mutation = useMutation({
    mutationFn: () => {
      const payload: Record<string, any> = {
        full_name: form.full_name,
        email: form.email,
        role_name: form.role_name,
        is_active: form.is_active,
      }
      if (form.password) payload.password = form.password
      return api.put(`/auth/users/${user.id}`, payload)
    },
    onSuccess: () => {
      toast.success('Usuario actualizado correctamente')
      qc.invalidateQueries({ queryKey: ['users'] })
      onClose()
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error al actualizar'),
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-lg font-semibold">Editar Usuario</h2>
            <p className="text-sm text-gray-500 font-mono">@{user.username}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
        </div>
        <div className="p-6 space-y-3">
          <div>
            <label className="label">Nombre Completo</label>
            <input className="input" value={form.full_name}
              onChange={e => setForm(f => ({...f, full_name: e.target.value}))} />
          </div>
          <div>
            <label className="label">Email</label>
            <input type="email" className="input" value={form.email}
              onChange={e => setForm(f => ({...f, email: e.target.value}))} />
          </div>
          <div>
            <label className="label">Rol</label>
            <select className="input" value={form.role_name}
              onChange={e => setForm(f => ({...f, role_name: e.target.value as 'admin' | 'vendedor' | 'rrhh' | 'contador'}))}>
              {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Nueva Contraseña <span className="text-gray-400 font-normal">(dejar vacío para no cambiar)</span></label>
            <input type="password" className="input" placeholder="••••••••" value={form.password}
              onChange={e => setForm(f => ({...f, password: e.target.value}))} />
          </div>
          <div className="flex items-center gap-3 pt-1">
            <label className="label mb-0">Estado</label>
            <button
              type="button"
              onClick={() => setForm(f => ({...f, is_active: !f.is_active}))}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${form.is_active ? 'bg-primary-600' : 'bg-gray-300'}`}
            >
              <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${form.is_active ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
            <span className="text-sm text-gray-600">{form.is_active ? 'Activo' : 'Inactivo'}</span>
          </div>
        </div>
        <div className="flex gap-2 px-6 pb-6">
          <button className="btn-primary flex-1" onClick={() => mutation.mutate()}
            disabled={!form.full_name || !form.email || mutation.isPending}>
            {mutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
          </button>
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  )
}

export default function UsersPage() {
  const [showForm, setShowForm] = useState(false)
  const [editUser, setEditUser] = useState<User | null>(null)

  const { data: users, isLoading, isError } = useQuery<User[]>({
    queryKey: ['users'],
    queryFn: () => api.get('/auth/users').then(r => r.data),
    retry: 1,
  })

  const roleColors: Record<string, string> = {
    admin:    'badge-red',
    vendedor: 'badge-blue',
    rrhh:     'badge-green',
    contador: 'badge-yellow',
  }

  const roleLabels: Record<string, string> = {
    admin:    'Administrador',
    vendedor: 'Vendedor',
    rrhh:     'RRHH',
    contador: 'Contador',
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
              <th className="px-4 py-3 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">Cargando usuarios...</td></tr>
            )}
            {isError && (
              <tr><td colSpan={6} className="text-center py-8 text-red-400">Error al cargar usuarios. Verifica que tengas permisos de administrador.</td></tr>
            )}
            {users?.map(u => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{u.full_name}</td>
                <td className="px-4 py-3 text-gray-600 font-mono text-xs">{u.username}</td>
                <td className="px-4 py-3 text-gray-600">{u.email}</td>
                <td className="px-4 py-3 text-center">
                  <span className={roleColors[u.role] || 'badge-gray'}>
                    {roleLabels[u.role] || u.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={u.is_active ? 'badge-green' : 'badge-gray'}>
                    {u.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-4 py-3 text-center">
                  <button
                    className="btn-secondary text-xs px-2 py-1 inline-flex items-center gap-1"
                    onClick={() => setEditUser(u)}
                  >
                    <Pencil size={12} /> Editar
                  </button>
                </td>
              </tr>
            ))}
            {!users?.length && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">No hay usuarios registrados</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {showForm && <UserForm onClose={() => setShowForm(false)} />}
      {editUser && <EditUserModal user={editUser} onClose={() => setEditUser(null)} />}
    </div>
  )
}
