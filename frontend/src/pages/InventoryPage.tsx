import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Package, AlertTriangle, Barcode } from 'lucide-react'
import { toast } from 'sonner'
import api from '../services/api'
import { Product, Category, PaginatedResponse } from '../types'
import clsx from 'clsx'

function fmtCLP(n: number): string {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n)
}

function ProductForm({ product, categories, onClose }: {
  product?: Product; categories: Category[]; onClose: () => void
}) {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    code: product?.code || '',
    barcode: product?.barcode || '',
    name: product?.name || '',
    description: product?.description || '',
    category_id: product?.category_id?.toString() || '',
    sale_price: product?.sale_price?.toString() || '',
    purchase_price: product?.purchase_price?.toString() || '0',
    stock_minimum: product?.stock_minimum?.toString() || '0',
    unit: product?.unit || 'unidad',
    afecto_iva: product?.afecto_iva ?? true,
  })

  const mutation = useMutation({
    mutationFn: (data: any) =>
      product
        ? api.put(`/products/${product.id}`, data)
        : api.post('/products', data),
    onSuccess: () => {
      toast.success(product ? 'Producto actualizado' : 'Producto creado')
      qc.invalidateQueries({ queryKey: ['products'] })
      onClose()
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error al guardar'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      ...form,
      category_id: form.category_id ? Number(form.category_id) : null,
      sale_price: Number(form.sale_price),
      purchase_price: Number(form.purchase_price),
      stock_minimum: Number(form.stock_minimum),
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">{product ? 'Editar Producto' : 'Nuevo Producto'}</h2>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Código *</label>
                <input className="input" value={form.code} onChange={e => setForm(f => ({...f, code: e.target.value}))} required />
              </div>
              <div>
                <label className="label">Código de Barras</label>
                <input className="input" value={form.barcode} onChange={e => setForm(f => ({...f, barcode: e.target.value}))} placeholder="EAN-13..." />
              </div>
            </div>
            <div>
              <label className="label">Nombre *</label>
              <input className="input" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
            </div>
            <div>
              <label className="label">Categoría</label>
              <select className="input" value={form.category_id} onChange={e => setForm(f => ({...f, category_id: e.target.value}))}>
                <option value="">Sin categoría</option>
                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Precio Compra (sin IVA)</label>
                <input type="number" className="input" value={form.purchase_price} onChange={e => setForm(f => ({...f, purchase_price: e.target.value}))} min="0" />
              </div>
              <div>
                <label className="label">Precio Venta (sin IVA) *</label>
                <input type="number" className="input" value={form.sale_price} onChange={e => setForm(f => ({...f, sale_price: e.target.value}))} min="0" required />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Stock Mínimo</label>
                <input type="number" className="input" value={form.stock_minimum} onChange={e => setForm(f => ({...f, stock_minimum: e.target.value}))} min="0" />
              </div>
              <div>
                <label className="label">Unidad</label>
                <select className="input" value={form.unit} onChange={e => setForm(f => ({...f, unit: e.target.value}))}>
                  <option value="unidad">Unidad</option>
                  <option value="kg">Kilogramo</option>
                  <option value="lt">Litro</option>
                  <option value="mt">Metro</option>
                  <option value="caja">Caja</option>
                </select>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="afecto_iva" checked={form.afecto_iva}
                onChange={e => setForm(f => ({...f, afecto_iva: e.target.checked}))} />
              <label htmlFor="afecto_iva" className="text-sm text-gray-700">Afecto a IVA (19%)</label>
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" className="btn-primary flex-1" disabled={mutation.isPending}>
                {mutation.isPending ? 'Guardando...' : 'Guardar'}
              </button>
              <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

function StockEntryModal({ product, onClose }: { product: Product; onClose: () => void }) {
  const qc = useQueryClient()
  const [qty, setQty] = useState('')
  const [cost, setCost] = useState('')
  const [notes, setNotes] = useState('')

  const mutation = useMutation({
    mutationFn: () => api.post('/products/stock-movements', {
      product_id: product.id,
      movement_type: 'entrada',
      quantity: Number(qty),
      unit_cost: cost ? Number(cost) : null,
      notes,
    }),
    onSuccess: () => {
      toast.success(`Entrada de ${qty} unidades registrada`)
      qc.invalidateQueries({ queryKey: ['products'] })
      onClose()
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error'),
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold mb-4">Entrada de Stock - {product.name}</h2>
        <div className="space-y-3">
          <div>
            <label className="label">Cantidad *</label>
            <input type="number" className="input" value={qty} onChange={e => setQty(e.target.value)} min="1" autoFocus required />
          </div>
          <div>
            <label className="label">Costo Unitario (opcional)</label>
            <input type="number" className="input" value={cost} onChange={e => setCost(e.target.value)} min="0" />
          </div>
          <div>
            <label className="label">Notas</label>
            <input className="input" value={notes} onChange={e => setNotes(e.target.value)} placeholder="Referencia, proveedor..." />
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button className="btn-primary flex-1" onClick={() => mutation.mutate()} disabled={!qty || mutation.isPending}>
            Registrar Entrada
          </button>
          <button className="btn-secondary" onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  )
}

export default function InventoryPage() {
  const [search, setSearch] = useState('')
  const [lowStock, setLowStock] = useState(false)
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [editProduct, setEditProduct] = useState<Product | undefined>()
  const [stockProduct, setStockProduct] = useState<Product | undefined>()
  const barcodeRef = useRef<HTMLInputElement>(null)
  const qc = useQueryClient()

  const { data: categories } = useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: () => api.get('/products/categories').then(r => r.data),
  })

  const { data, isLoading } = useQuery<PaginatedResponse<Product>>({
    queryKey: ['products', page, search, lowStock],
    queryFn: () => api.get(`/products?page=${page}&search=${search}&low_stock=${lowStock}`).then(r => r.data),
  })

  const handleBarcodeSearch = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const barcode = (e.target as HTMLInputElement).value.trim()
      if (!barcode) return
      try {
        const { data: product } = await api.get<Product>(`/products/barcode/${barcode}`)
        setStockProduct(product)
        ;(e.target as HTMLInputElement).value = ''
      } catch {
        toast.error(`Producto con código ${barcode} no encontrado`)
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventario</h1>
          <p className="text-gray-500 text-sm mt-1">{data?.total || 0} productos</p>
        </div>
        <button className="btn-primary" onClick={() => { setEditProduct(undefined); setShowForm(true) }}>
          <Plus size={16} /> Nuevo Producto
        </button>
      </div>

      <div className="card">
        <div className="flex gap-3 flex-wrap">
          <div className="relative flex-1 min-w-48">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input className="input pl-9" placeholder="Buscar por nombre, código..." value={search}
              onChange={e => { setSearch(e.target.value); setPage(1) }} />
          </div>
          <div className="relative min-w-48">
            <Barcode size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input ref={barcodeRef} className="input pl-9" placeholder="Escanear código de barras..." onKeyDown={handleBarcodeSearch} />
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" checked={lowStock} onChange={e => setLowStock(e.target.checked)} />
            Solo stock bajo
          </label>
        </div>
      </div>

      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="table-header">
              <tr>
                <th className="px-4 py-3 text-left">Producto</th>
                <th className="px-4 py-3 text-left">Código</th>
                <th className="px-4 py-3 text-left">Categoría</th>
                <th className="px-4 py-3 text-right">P. Venta c/IVA</th>
                <th className="px-4 py-3 text-center">Stock</th>
                <th className="px-4 py-3 text-center">Estado</th>
                <th className="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {isLoading && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">Cargando...</td></tr>
              )}
              {data?.items.map(p => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">{p.name}</div>
                    {p.barcode && <div className="text-xs text-gray-400">{p.barcode}</div>}
                  </td>
                  <td className="px-4 py-3 text-gray-600 font-mono text-xs">{p.code}</td>
                  <td className="px-4 py-3">
                    {p.category && <span className="badge-blue">{p.category.name}</span>}
                  </td>
                  <td className="px-4 py-3 text-right font-medium">{fmtCLP(p.sale_price_with_iva)}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={clsx(
                      'font-bold',
                      p.stock_current <= p.stock_minimum ? 'text-red-600' : 'text-gray-900'
                    )}>
                      {p.stock_current} {p.unit}
                    </span>
                    {p.stock_current <= p.stock_minimum && (
                      <AlertTriangle size={12} className="inline ml-1 text-red-500" />
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={p.is_active ? 'badge-green' : 'badge-gray'}>
                      {p.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex gap-1 justify-center">
                      <button className="btn-secondary text-xs px-2 py-1" onClick={() => setStockProduct(p)}>
                        + Stock
                      </button>
                      <button className="btn-secondary text-xs px-2 py-1" onClick={() => { setEditProduct(p); setShowForm(true) }}>
                        Editar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!isLoading && data?.items.length === 0 && (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                  <Package size={32} className="mx-auto mb-2 opacity-30" />
                  No se encontraron productos
                </td></tr>
              )}
            </tbody>
          </table>
        </div>

        {data && data.pages > 1 && (
          <div className="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
            <p className="text-sm text-gray-500">Página {page} de {data.pages} ({data.total} total)</p>
            <div className="flex gap-2">
              <button className="btn-secondary text-xs" onClick={() => setPage(p => p - 1)} disabled={page === 1}>Anterior</button>
              <button className="btn-secondary text-xs" onClick={() => setPage(p => p + 1)} disabled={page === data.pages}>Siguiente</button>
            </div>
          </div>
        )}
      </div>

      {showForm && (
        <ProductForm
          product={editProduct}
          categories={categories || []}
          onClose={() => { setShowForm(false); setEditProduct(undefined) }}
        />
      )}
      {stockProduct && (
        <StockEntryModal product={stockProduct} onClose={() => setStockProduct(undefined)} />
      )}
    </div>
  )
}
