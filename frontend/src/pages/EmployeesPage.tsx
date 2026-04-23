import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, FileText, X } from 'lucide-react'
import { toast } from 'sonner'
import api from '../services/api'
import { Employee, VacationRequest } from '../types'
import clsx from 'clsx'

const AFP_OPTIONS = ['Capital', 'Cuprum', 'Habitat', 'Modelo', 'PlanVital', 'ProVida', 'Uno']
const ISAPRE_OPTIONS = ['FONASA', 'Banmédica', 'Colmena', 'Consalud', 'Cruz Blanca', 'Esencial', 'Masvida', 'Nueva Masvida', 'Vida Tres']

function formatRut(value: string): string {
  const clean = value.replace(/[^0-9kK]/g, '').toUpperCase()
  if (clean.length < 2) return clean
  const body = clean.slice(0, -1)
  const dv = clean.slice(-1)
  const formatted = body.replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  return `${formatted}-${dv}`
}

function validateRut(rut: string): boolean {
  const clean = rut.replace(/[^0-9kK]/g, '').toUpperCase()
  if (clean.length < 2) return false
  const body = clean.slice(0, -1)
  const dv = clean.slice(-1)
  let sum = 0
  let mult = 2
  for (let i = body.length - 1; i >= 0; i--) {
    sum += parseInt(body[i]) * mult
    mult = mult === 7 ? 2 : mult + 1
  }
  const remainder = 11 - (sum % 11)
  const expected = remainder === 11 ? '0' : remainder === 10 ? 'K' : remainder.toString()
  return dv === expected
}

const EMPTY_FORM = {
  rut: '', first_name: '', last_name: '', email: '', phone: '',
  address: '', birth_date: '', gender: '', position: '', department: '',
  afp: '', isapre: '', isapre_amount: '', banco: '',
  cuenta_bancaria: '', tipo_cuenta: '', vacation_days_per_year: '15',
}

function EmployeeModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient()
  const [form, setForm] = useState(EMPTY_FORM)
  const [rutTouched, setRutTouched] = useState(false)
  const firstRef = useRef<HTMLInputElement>(null)

  const rutValid = !rutTouched || form.rut === '' || validateRut(form.rut)
  const rutError = rutTouched && form.rut !== '' && !validateRut(form.rut)

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm(f => ({ ...f, [k]: e.target.value }))

  const handleRutChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/[^0-9kK]/g, '').toUpperCase()
    setForm(f => ({ ...f, rut: raw }))
  }

  const handleRutBlur = () => {
    setRutTouched(true)
    if (form.rut) {
      setForm(f => ({ ...f, rut: formatRut(f.rut) }))
    }
  }

  const mutation = useMutation({
    mutationFn: () => {
      const payload: Record<string, any> = {
        rut: form.rut,
        first_name: form.first_name,
        last_name: form.last_name,
        position: form.position,
        vacation_days_per_year: Number(form.vacation_days_per_year),
      }
      if (form.email) payload.email = form.email
      if (form.phone) payload.phone = form.phone
      if (form.address) payload.address = form.address
      if (form.birth_date) payload.birth_date = form.birth_date
      if (form.gender) payload.gender = form.gender
      if (form.department) payload.department = form.department
      if (form.afp) payload.afp = form.afp
      if (form.isapre) payload.isapre = form.isapre
      if (form.isapre_amount) payload.isapre_amount = Number(form.isapre_amount)
      if (form.banco) payload.banco = form.banco
      if (form.cuenta_bancaria) payload.cuenta_bancaria = form.cuenta_bancaria
      if (form.tipo_cuenta) payload.tipo_cuenta = form.tipo_cuenta
      return api.post('/employees', payload)
    },
    onSuccess: () => {
      toast.success('Empleado creado correctamente')
      qc.invalidateQueries({ queryKey: ['employees'] })
      onClose()
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error al crear empleado'),
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Nuevo Empleado</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600"><X size={20} /></button>
        </div>

        <div className="p-6 space-y-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Datos Personales</p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">RUT *</label>
              <input
                ref={firstRef}
                className={clsx('input', rutError && 'border-red-500 focus:ring-red-500 focus:border-red-500')}
                placeholder="12.345.678-9"
                value={form.rut}
                onChange={handleRutChange}
                onBlur={handleRutBlur}
                required
                autoFocus
              />
              {rutError && (
                <p className="text-red-500 text-xs mt-1">RUT inválido. Verifica el dígito verificador.</p>
              )}
            </div>
            <div>
              <label className="label">Género</label>
              <select className="input" value={form.gender} onChange={set('gender')}>
                <option value="">Sin especificar</option>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
                <option value="O">Otro</option>
              </select>
            </div>
            <div>
              <label className="label">Nombres *</label>
              <input className="input" placeholder="Juan" value={form.first_name} onChange={set('first_name')} required />
            </div>
            <div>
              <label className="label">Apellidos *</label>
              <input className="input" placeholder="Pérez González" value={form.last_name} onChange={set('last_name')} required />
            </div>
            <div>
              <label className="label">Email</label>
              <input type="email" className="input" placeholder="juan@empresa.cl" value={form.email} onChange={set('email')} />
            </div>
            <div>
              <label className="label">Teléfono</label>
              <input className="input" placeholder="+56 9 1234 5678" value={form.phone} onChange={set('phone')} />
            </div>
            <div>
              <label className="label">Fecha de Nacimiento</label>
              <input type="date" className="input" value={form.birth_date} onChange={set('birth_date')} />
            </div>
            <div>
              <label className="label">Dirección</label>
              <input className="input" placeholder="Av. Ejemplo 123, Santiago" value={form.address} onChange={set('address')} />
            </div>
          </div>

          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide pt-2">Datos Laborales</p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Cargo *</label>
              <input className="input" placeholder="Vendedor, Bodeguero..." value={form.position} onChange={set('position')} required />
            </div>
            <div>
              <label className="label">Departamento</label>
              <input className="input" placeholder="Ventas, Administración..." value={form.department} onChange={set('department')} />
            </div>
            <div>
              <label className="label">Días vacaciones / año</label>
              <input type="number" className="input" value={form.vacation_days_per_year} onChange={set('vacation_days_per_year')} min="15" />
            </div>
          </div>

          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide pt-2">Previsión</p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">AFP</label>
              <select className="input" value={form.afp} onChange={set('afp')}>
                <option value="">Seleccionar AFP</option>
                {AFP_OPTIONS.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </div>
            <div>
              <label className="label">ISAPRE / Fonasa</label>
              <select className="input" value={form.isapre} onChange={set('isapre')}>
                <option value="">Seleccionar</option>
                {ISAPRE_OPTIONS.map(i => <option key={i} value={i}>{i}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Monto ISAPRE (mensual)</label>
              <input type="number" className="input" placeholder="0" value={form.isapre_amount} onChange={set('isapre_amount')} />
            </div>
          </div>

          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide pt-2">Datos Bancarios</p>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Banco</label>
              <input className="input" placeholder="Banco Estado, Santander..." value={form.banco} onChange={set('banco')} />
            </div>
            <div>
              <label className="label">Tipo de Cuenta</label>
              <select className="input" value={form.tipo_cuenta} onChange={set('tipo_cuenta')}>
                <option value="">Seleccionar</option>
                <option value="Cuenta Corriente">Cuenta Corriente</option>
                <option value="Cuenta Vista">Cuenta Vista / RUT</option>
                <option value="Cuenta Ahorro">Cuenta Ahorro</option>
              </select>
            </div>
            <div className="col-span-2">
              <label className="label">N° de Cuenta</label>
              <input className="input" placeholder="00012345678" value={form.cuenta_bancaria} onChange={set('cuenta_bancaria')} />
            </div>
          </div>
        </div>

        <div className="flex gap-2 p-6 border-t">
          <button
            className="btn-primary flex-1"
            disabled={!form.rut || !validateRut(form.rut) || !form.first_name || !form.last_name || !form.position || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {mutation.isPending ? 'Guardando...' : 'Crear Empleado'}
          </button>
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  )
}

function fmtCLP(n: number): string {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n)
}

const MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

type Tab = 'employees' | 'salaries' | 'vacations'

function SalaryModal({ employee, onClose }: { employee: Employee; onClose: () => void }) {
  const qc = useQueryClient()
  const now = new Date()
  const [form, setForm] = useState({
    period_year: now.getFullYear().toString(),
    period_month: (now.getMonth() + 1).toString(),
    sueldo_base: '',
    horas_extra: '0',
    valor_hora_extra: '0',
    bono_colacion: '0',
    bono_movilizacion: '0',
    otros_haberes: '0',
    otros_descuentos: '0',
  })

  const mutation = useMutation({
    mutationFn: () => api.post('/employees/salary-payments', {
      employee_id: employee.id,
      ...Object.fromEntries(Object.entries(form).map(([k, v]) => [k, Number(v)])),
    }),
    onSuccess: () => {
      toast.success('Liquidación generada correctamente')
      qc.invalidateQueries({ queryKey: ['salary-payments'] })
      onClose()
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error'),
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-lg font-semibold mb-1">Generar Liquidación</h2>
        <p className="text-sm text-gray-500 mb-4">{employee.first_name} {employee.last_name}</p>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Año</label>
              <input type="number" className="input" value={form.period_year} onChange={e => setForm(f => ({...f, period_year: e.target.value}))} />
            </div>
            <div>
              <label className="label">Mes</label>
              <select className="input" value={form.period_month} onChange={e => setForm(f => ({...f, period_month: e.target.value}))}>
                {MESES.slice(1).map((m, i) => <option key={i+1} value={i+1}>{m}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="label">Sueldo Base *</label>
            <input type="number" className="input" value={form.sueldo_base} onChange={e => setForm(f => ({...f, sueldo_base: e.target.value}))} required />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Horas Extra</label>
              <input type="number" className="input" value={form.horas_extra} onChange={e => setForm(f => ({...f, horas_extra: e.target.value}))} />
            </div>
            <div>
              <label className="label">Valor Hora Extra</label>
              <input type="number" className="input" value={form.valor_hora_extra} onChange={e => setForm(f => ({...f, valor_hora_extra: e.target.value}))} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Bono Colación</label>
              <input type="number" className="input" value={form.bono_colacion} onChange={e => setForm(f => ({...f, bono_colacion: e.target.value}))} />
            </div>
            <div>
              <label className="label">Bono Movilización</label>
              <input type="number" className="input" value={form.bono_movilizacion} onChange={e => setForm(f => ({...f, bono_movilizacion: e.target.value}))} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Otros Haberes</label>
              <input type="number" className="input" value={form.otros_haberes} onChange={e => setForm(f => ({...f, otros_haberes: e.target.value}))} />
            </div>
            <div>
              <label className="label">Otros Descuentos</label>
              <input type="number" className="input" value={form.otros_descuentos} onChange={e => setForm(f => ({...f, otros_descuentos: e.target.value}))} />
            </div>
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button className="btn-primary flex-1" onClick={() => mutation.mutate()} disabled={!form.sueldo_base || mutation.isPending}>
            {mutation.isPending ? 'Generando...' : 'Generar Liquidación PDF'}
          </button>
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  )
}

export default function EmployeesPage() {
  const [tab, setTab] = useState<Tab>('employees')
  const [showForm, setShowForm] = useState(false)
  const [salaryEmployee, setSalaryEmployee] = useState<Employee | undefined>()
  const qc = useQueryClient()

  const { data: employees } = useQuery<Employee[]>({
    queryKey: ['employees'],
    queryFn: () => api.get('/employees').then(r => r.data),
  })

  const { data: vacations } = useQuery<VacationRequest[]>({
    queryKey: ['vacation-requests'],
    queryFn: () => api.get('/employees/vacation-requests').then(r => r.data),
    enabled: tab === 'vacations',
  })

  const approveVacation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.put(`/employees/vacation-requests/${id}`, { status }),
    onSuccess: () => { toast.success('Solicitud actualizada'); qc.invalidateQueries({ queryKey: ['vacation-requests'] }) },
  })

  const tabs = [
    { key: 'employees', label: 'Empleados' },
    { key: 'salaries', label: 'Liquidaciones' },
    { key: 'vacations', label: 'Vacaciones' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Recursos Humanos</h1>
        {tab === 'employees' && (
          <button className="btn-primary" onClick={() => setShowForm(true)}>
            <Plus size={16} /> Nuevo Empleado
          </button>
        )}
      </div>

      <div className="flex border-b border-gray-200">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key as Tab)}
            className={clsx('px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              tab === t.key ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700')}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'employees' && (
        <div className="card overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead className="table-header">
              <tr>
                <th className="px-4 py-3 text-left">Empleado</th>
                <th className="px-4 py-3 text-left">RUT</th>
                <th className="px-4 py-3 text-left">Cargo</th>
                <th className="px-4 py-3 text-left">AFP</th>
                <th className="px-4 py-3 text-left">ISAPRE</th>
                <th className="px-4 py-3 text-center">Días Vacac.</th>
                <th className="px-4 py-3 text-center">Estado</th>
                <th className="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {employees?.map(emp => (
                <tr key={emp.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{emp.first_name} {emp.last_name}</td>
                  <td className="px-4 py-3 font-mono text-xs">{emp.rut}</td>
                  <td className="px-4 py-3 text-gray-600">{emp.position}</td>
                  <td className="px-4 py-3 text-gray-600 text-xs">{emp.afp || '-'}</td>
                  <td className="px-4 py-3 text-gray-600 text-xs">{emp.isapre || '-'}</td>
                  <td className="px-4 py-3 text-center">{Number(emp.vacation_days_available).toFixed(1)}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={emp.is_active ? 'badge-green' : 'badge-gray'}>
                      {emp.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button className="btn-secondary text-xs px-2 py-1" onClick={() => setSalaryEmployee(emp)}>
                      <FileText size={12} /> Liquidación
                    </button>
                  </td>
                </tr>
              ))}
              {!employees?.length && (
                <tr><td colSpan={8} className="text-center py-8 text-gray-400">No hay empleados registrados</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'vacations' && (
        <div className="card overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead className="table-header">
              <tr>
                <th className="px-4 py-3 text-left">Empleado</th>
                <th className="px-4 py-3 text-left">Período</th>
                <th className="px-4 py-3 text-center">Días</th>
                <th className="px-4 py-3 text-left">Motivo</th>
                <th className="px-4 py-3 text-center">Estado</th>
                <th className="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {vacations?.map(v => {
                const emp = employees?.find(e => e.id === v.employee_id)
                return (
                  <tr key={v.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium">{emp ? `${emp.first_name} ${emp.last_name}` : `#${v.employee_id}`}</td>
                    <td className="px-4 py-3 text-gray-600 text-xs">{v.start_date} → {v.end_date}</td>
                    <td className="px-4 py-3 text-center font-medium">{v.days_requested}</td>
                    <td className="px-4 py-3 text-gray-600 text-xs">{v.reason || '-'}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={clsx('badge', {
                        'badge-yellow': v.status === 'pendiente',
                        'badge-green': v.status === 'aprobada',
                        'badge-red': v.status === 'rechazada',
                        'badge-blue': v.status === 'tomada',
                      })}>
                        {v.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {v.status === 'pendiente' && (
                        <div className="flex gap-1 justify-center">
                          <button className="btn-primary text-xs px-2 py-1"
                            onClick={() => approveVacation.mutate({ id: v.id, status: 'aprobada' })}>
                            Aprobar
                          </button>
                          <button className="btn-danger text-xs px-2 py-1"
                            onClick={() => approveVacation.mutate({ id: v.id, status: 'rechazada' })}>
                            Rechazar
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
              {!vacations?.length && (
                <tr><td colSpan={6} className="text-center py-8 text-gray-400">No hay solicitudes de vacaciones</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {showForm && <EmployeeModal onClose={() => setShowForm(false)} />}

      {salaryEmployee && (
        <SalaryModal employee={salaryEmployee} onClose={() => setSalaryEmployee(undefined)} />
      )}
    </div>
  )
}
