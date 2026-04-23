import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Printer, XCircle } from 'lucide-react'
import { toast } from 'sonner'
import api from '../services/api'
import { Sale, PaginatedResponse } from '../types'
import clsx from 'clsx'

function fmtCLP(n: number): string {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n)
}

const statusBadge = {
  completada: 'badge-green',
  pendiente: 'badge-yellow',
  anulada: 'badge-red',
}

const MESES = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

export default function SalesPage() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [page, setPage] = useState(1)
  const qc = useQueryClient()

  const { data, isLoading } = useQuery<PaginatedResponse<Sale>>({
    queryKey: ['sales', page, year, month],
    queryFn: () => api.get(`/sales?page=${page}&year=${year}&month=${month}`).then(r => r.data),
  })

  const cancelMutation = useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) =>
      api.post(`/sales/${id}/cancel?reason=${encodeURIComponent(reason)}`),
    onSuccess: () => {
      toast.success('Venta anulada')
      qc.invalidateQueries({ queryKey: ['sales'] })
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error'),
  })

  const handleCancel = (sale: Sale) => {
    const reason = window.prompt('Motivo de anulación:')
    if (!reason) return
    cancelMutation.mutate({ id: sale.id, reason })
  }

  const total = data?.items.reduce((sum, s) => s.status !== 'anulada' ? sum + Number(s.total) : sum, 0) || 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Historial de Ventas</h1>
        <div className="flex gap-2">
          <select className="input w-auto" value={month} onChange={e => setMonth(Number(e.target.value))}>
            {MESES.slice(1).map((m, i) => <option key={i+1} value={i+1}>{m}</option>)}
          </select>
          <select className="input w-auto" value={year} onChange={e => setYear(Number(e.target.value))}>
            {[2024, 2025, 2026].map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>

      <div className="card">
        <p className="text-sm text-gray-500">Total del período (ventas completadas)</p>
        <p className="text-2xl font-bold text-gray-900">{fmtCLP(total)}</p>
      </div>

      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="table-header">
              <tr>
                <th className="px-4 py-3 text-left">ID</th>
                <th className="px-4 py-3 text-left">Fecha</th>
                <th className="px-4 py-3 text-left">Cliente</th>
                <th className="px-4 py-3 text-right">Subtotal</th>
                <th className="px-4 py-3 text-right">IVA</th>
                <th className="px-4 py-3 text-right">Total</th>
                <th className="px-4 py-3 text-center">Estado</th>
                <th className="px-4 py-3 text-center">DTE</th>
                <th className="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading && <tr><td colSpan={9} className="text-center py-8 text-gray-400">Cargando...</td></tr>}
              {data?.items.map(sale => (
                <tr key={sale.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-xs">#{sale.id}</td>
                  <td className="px-4 py-3 text-gray-600">
                    {new Date(sale.created_at).toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {sale.customer_name || 'Consumidor Final'}
                    {sale.customer_rut && <span className="text-xs text-gray-400 block">{sale.customer_rut}</span>}
                  </td>
                  <td className="px-4 py-3 text-right">{fmtCLP(Number(sale.subtotal))}</td>
                  <td className="px-4 py-3 text-right">{fmtCLP(Number(sale.iva_amount))}</td>
                  <td className="px-4 py-3 text-right font-bold">{fmtCLP(Number(sale.total))}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={statusBadge[sale.status] || 'badge-gray'}>{sale.status}</span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {sale.dte_enviado
                      ? <span className="badge-green">Enviado</span>
                      : <span className="badge-gray">No</span>
                    }
                  </td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex gap-1 justify-center">
                      <button className="text-primary-600 hover:text-primary-800" title="Imprimir boleta"
                        onClick={() => window.open(`/api/sales/${sale.id}/receipt`, '_blank')}>
                        <Printer size={16} />
                      </button>
                      {sale.status === 'completada' && (
                        <button className="text-red-400 hover:text-red-600" title="Anular venta"
                          onClick={() => handleCancel(sale)}>
                          <XCircle size={16} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {!isLoading && !data?.items.length && (
                <tr><td colSpan={9} className="text-center py-8 text-gray-400">No hay ventas en este período</td></tr>
              )}
            </tbody>
          </table>
        </div>
        {data && data.pages > 1 && (
          <div className="px-4 py-3 border-t border-gray-100 flex justify-between items-center">
            <span className="text-sm text-gray-500">Página {page} de {data.pages}</span>
            <div className="flex gap-2">
              <button className="btn-secondary text-xs" onClick={() => setPage(p => p-1)} disabled={page === 1}>Anterior</button>
              <button className="btn-secondary text-xs" onClick={() => setPage(p => p+1)} disabled={page === data.pages}>Siguiente</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
