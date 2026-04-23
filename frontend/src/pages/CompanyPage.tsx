import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import api from '../services/api'
import { Company } from '../types'

export default function CompanyPage() {
  const qc = useQueryClient()
  const { data: company } = useQuery<Company>({
    queryKey: ['company'],
    queryFn: () => api.get('/company').then(r => r.data),
  })

  const [form, setForm] = useState<Partial<Company>>({
    rut: '', razon_social: '', nombre_fantasia: '', giro: '',
    direccion: '', comuna: '', ciudad: '', telefono: '', email: '',
    sii_ambiente: 'certificacion', sii_resolucion_numero: '',
    iva_porcentaje: 19, notas_boleta: '',
  })

  useEffect(() => {
    if (company) setForm(company)
  }, [company])

  const mutation = useMutation({
    mutationFn: () => api.put('/company', form),
    onSuccess: () => { toast.success('Datos guardados'); qc.invalidateQueries({ queryKey: ['company'] }) },
    onError: () => toast.error('Error al guardar'),
  })

  const f = (key: keyof Company) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setForm(prev => ({ ...prev, [key]: e.target.value }))
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-900">Configuración de Empresa</h1>

      <div className="card space-y-4">
        <h2 className="font-semibold text-gray-900">Datos Tributarios</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">RUT Empresa *</label>
            <input className="input" value={form.rut || ''} onChange={f('rut')} placeholder="12.345.678-9" />
          </div>
          <div>
            <label className="label">Razón Social *</label>
            <input className="input" value={form.razon_social || ''} onChange={f('razon_social')} />
          </div>
          <div>
            <label className="label">Nombre de Fantasía</label>
            <input className="input" value={form.nombre_fantasia || ''} onChange={f('nombre_fantasia')} />
          </div>
          <div>
            <label className="label">Giro Comercial</label>
            <input className="input" value={form.giro || ''} onChange={f('giro')} placeholder="Comercio al por menor" />
          </div>
        </div>
      </div>

      <div className="card space-y-4">
        <h2 className="font-semibold text-gray-900">Dirección y Contacto</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="label">Dirección</label>
            <input className="input" value={form.direccion || ''} onChange={f('direccion')} />
          </div>
          <div>
            <label className="label">Comuna</label>
            <input className="input" value={form.comuna || ''} onChange={f('comuna')} />
          </div>
          <div>
            <label className="label">Ciudad</label>
            <input className="input" value={form.ciudad || ''} onChange={f('ciudad')} />
          </div>
          <div>
            <label className="label">Teléfono</label>
            <input className="input" value={form.telefono || ''} onChange={f('telefono')} />
          </div>
          <div>
            <label className="label">Email</label>
            <input type="email" className="input" value={form.email || ''} onChange={f('email')} />
          </div>
        </div>
      </div>

      <div className="card space-y-4">
        <h2 className="font-semibold text-gray-900">Integración SII</h2>
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
          <strong>Para emitir boletas electrónicas necesitas:</strong>
          <ol className="list-decimal ml-4 mt-2 space-y-1">
            <li>Certificado digital de firma electrónica (pfx/p12)</li>
            <li>Registro del RUT como emisor DTE en el SII</li>
            <li>Resolución de emisor DTE del SII</li>
          </ol>
          <p className="mt-2">Más información en <a href="https://www.sii.cl" target="_blank" rel="noopener" className="underline font-medium">sii.cl</a></p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Ambiente SII</label>
            <select className="input" value={form.sii_ambiente || 'certificacion'} onChange={f('sii_ambiente')}>
              <option value="certificacion">Certificación (pruebas)</option>
              <option value="produccion">Producción (real)</option>
            </select>
          </div>
          <div>
            <label className="label">N° Resolución SII</label>
            <input className="input" value={form.sii_resolucion_numero || ''} onChange={f('sii_resolucion_numero')} placeholder="Ej: 80" />
          </div>
        </div>
        <div>
          <label className="label">Notas en Boleta</label>
          <textarea className="input h-20 resize-none" value={form.notas_boleta || ''} onChange={f('notas_boleta')}
            placeholder="Texto que aparecerá al pie de cada boleta..." />
        </div>
      </div>

      <button className="btn-primary" onClick={() => mutation.mutate()} disabled={mutation.isPending}>
        {mutation.isPending ? 'Guardando...' : 'Guardar Configuración'}
      </button>
    </div>
  )
}
