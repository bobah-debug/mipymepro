import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import api from '../services/api'
import { DashboardData } from '../types'
import { TrendingUp, TrendingDown, ShoppingCart, DollarSign, Package, Users } from 'lucide-react'
import clsx from 'clsx'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

function fmtCLP(n: number): string {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n)
}

function KPICard({ title, value, prev, icon: Icon, format = 'clp' }: {
  title: string; value: number; prev?: number; icon: any; format?: 'clp' | 'number'
}) {
  const pct = prev && prev > 0 ? ((value - prev) / prev) * 100 : null
  const up = pct !== null && pct >= 0
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-500 font-medium">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">
            {format === 'clp' ? fmtCLP(value) : value.toLocaleString('es-CL')}
          </p>
          {pct !== null && (
            <div className={clsx('flex items-center gap-1 mt-1 text-sm', up ? 'text-green-600' : 'text-red-600')}>
              {up ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
              {Math.abs(pct).toFixed(1)}% vs mes anterior
            </div>
          )}
        </div>
        <div className="p-3 bg-primary-50 rounded-xl">
          <Icon size={20} className="text-primary-600" />
        </div>
      </div>
    </div>
  )
}

const MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

export default function DashboardPage() {
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)

  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard', year, month],
    queryFn: () => api.get(`/dashboard?year=${year}&month=${month}`).then(r => r.data),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  const kpis = data?.kpis
  const dailySales = data?.daily_sales.map(d => ({
    ...d,
    date: d.date.split('-')[2],
    total: Number(d.total),
  })) || []
  const topProducts = data?.top_products.map(p => ({ ...p, total: Number(p.total) })) || []
  const catSales = data?.category_sales.map(c => ({ ...c, total: Number(c.total) })) || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">{MESES[month]} {year}</p>
        </div>
        <div className="flex gap-2">
          <select className="input w-auto" value={month} onChange={e => setMonth(Number(e.target.value))}>
            {MESES.slice(1).map((m, i) => (
              <option key={i + 1} value={i + 1}>{m}</option>
            ))}
          </select>
          <select className="input w-auto" value={year} onChange={e => setYear(Number(e.target.value))}>
            {[2024, 2025, 2026, 2027].map(y => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
      </div>

      {kpis && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard title="Ventas del Mes" value={Number(kpis.total_ventas)} prev={Number(kpis.total_ventas_prev)} icon={DollarSign} />
          <KPICard title="Número de Ventas" value={kpis.num_ventas} icon={ShoppingCart} format="number" />
          <KPICard title="Ticket Promedio" value={Number(kpis.ticket_promedio)} icon={TrendingUp} />
          <KPICard title="Utilidad Bruta" value={Number(kpis.utilidad_bruta)} icon={TrendingUp} />
        </div>
      )}

      {kpis && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <p className="text-sm text-gray-500">Gastos en Sueldos</p>
            <p className="text-xl font-bold text-gray-900">{fmtCLP(Number(kpis.total_gastos_sueldos))}</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-500">Margen Bruto</p>
            <p className="text-xl font-bold text-gray-900">{kpis.margen_bruto_pct.toFixed(1)}%</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-500">Productos Bajo Stock</p>
            <p className={clsx('text-xl font-bold', kpis.productos_bajo_stock > 0 ? 'text-red-600' : 'text-green-600')}>
              {kpis.productos_bajo_stock}
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Ventas Diarias</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={dailySales}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: any) => fmtCLP(v)} />
              <Line type="monotone" dataKey="total" stroke="#3b82f6" strokeWidth={2} dot={false} name="Total" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Top 10 Productos</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={topProducts.slice(0, 10)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="product_name" tick={{ fontSize: 10 }} width={100} />
              <Tooltip formatter={(v: any) => fmtCLP(v)} />
              <Bar dataKey="total" fill="#3b82f6" name="Total" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card lg:col-span-2">
          <h3 className="font-semibold text-gray-900 mb-4">Ventas por Categoría</h3>
          <div className="flex items-center gap-8">
            <ResponsiveContainer width="40%" height={220}>
              <PieChart>
                <Pie data={catSales} dataKey="total" nameKey="category_name" cx="50%" cy="50%" outerRadius={80} label={({ percentage }) => `${percentage.toFixed(0)}%`}>
                  {catSales.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: any) => fmtCLP(v)} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-2">
              {catSales.map((c, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className="text-sm text-gray-600 flex-1">{c.category_name}</span>
                  <span className="text-sm font-medium">{fmtCLP(c.total)}</span>
                  <span className="text-xs text-gray-400">{c.percentage.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
