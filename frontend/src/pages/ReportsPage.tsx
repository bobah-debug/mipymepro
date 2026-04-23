import { useState } from 'react'
import { Download, FileSpreadsheet, FileText } from 'lucide-react'
import { toast } from 'sonner'
import api from '../services/api'

const MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

function downloadBlob(data: any, filename: string, mimeType: string) {
  const url = window.URL.createObjectURL(new Blob([data], { type: mimeType }))
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  window.URL.revokeObjectURL(url)
}

export default function ReportsPage() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [loading, setLoading] = useState<string | null>(null)

  const download = async (key: string, url: string, filename: string, mime: string) => {
    setLoading(key)
    try {
      const res = await api.get(url, { responseType: 'arraybuffer' })
      downloadBlob(res.data, filename, mime)
      toast.success('Archivo descargado')
    } catch {
      toast.error('Error al descargar')
    } finally {
      setLoading(null)
    }
  }

  const reports = [
    {
      key: 'inventory-excel',
      title: 'Inventario Excel',
      description: 'Exporta todo el inventario de productos con stock, precios y categorías. Formato compatible con contabilidad.',
      icon: FileSpreadsheet,
      color: 'text-green-600',
      action: () => download('inventory-excel', '/reports/inventory/excel', 'inventario.xlsx',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    },
    {
      key: 'inventory-csv',
      title: 'Inventario CSV',
      description: 'Inventario en formato CSV para importar en cualquier software contable.',
      icon: FileText,
      color: 'text-blue-600',
      action: () => download('inventory-csv', '/reports/inventory/csv', 'inventario.csv', 'text/csv'),
    },
    {
      key: 'sales-excel',
      title: 'Ventas del Período Excel',
      description: `Exporta todas las ventas del período seleccionado: ${MESES[month]} ${year}`,
      icon: FileSpreadsheet,
      color: 'text-green-600',
      action: () => download('sales-excel', `/reports/sales/excel?year=${year}&month=${month}`,
        `ventas_${year}_${String(month).padStart(2, '0')}.xlsx`,
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    },
    {
      key: 'salary-pdf',
      title: 'Liquidaciones en Lote PDF',
      description: `Descarga todas las liquidaciones de ${MESES[month]} ${year} en un archivo ZIP.`,
      icon: Download,
      color: 'text-red-600',
      action: () => download('salary-pdf', `/reports/salary-payments/bulk-pdf?year=${year}&month=${month}`,
        `liquidaciones_${year}_${String(month).padStart(2, '0')}.zip`, 'application/zip'),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Reportes y Exportación</h1>
        <div className="flex gap-2">
          <select className="input w-auto" value={month} onChange={e => setMonth(Number(e.target.value))}>
            {MESES.slice(1).map((m, i) => <option key={i+1} value={i+1}>{m}</option>)}
          </select>
          <select className="input w-auto" value={year} onChange={e => setYear(Number(e.target.value))}>
            {[2024, 2025, 2026].map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reports.map(r => (
          <div key={r.key} className="card hover:shadow-md transition-shadow">
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-xl bg-gray-50`}>
                <r.icon size={24} className={r.color} />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900">{r.title}</h3>
                <p className="text-sm text-gray-500 mt-1">{r.description}</p>
              </div>
            </div>
            <button
              className="btn-primary w-full mt-4"
              onClick={r.action}
              disabled={loading === r.key}
            >
              {loading === r.key ? (
                <><span className="animate-spin inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full" /> Descargando...</>
              ) : (
                <><Download size={16} /> Descargar</>
              )}
            </button>
          </div>
        ))}
      </div>

      <div className="card bg-blue-50 border-blue-100">
        <h3 className="font-semibold text-blue-900 mb-2">📋 Libro de Ventas SII</h3>
        <p className="text-sm text-blue-700">
          Para el Formulario 29 del SII, exporta el archivo de ventas Excel del período y envíalo a tu contador.
          Los campos incluyen: folio, fecha, RUT cliente, neto, IVA, total y estado DTE.
        </p>
      </div>
    </div>
  )
}
