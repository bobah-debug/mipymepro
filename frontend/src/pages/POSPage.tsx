import { useState, useRef, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Search, Barcode, Trash2, Plus, Minus, Printer, ShoppingBag } from 'lucide-react'
import { toast } from 'sonner'
import api from '../services/api'
import { Product, PaymentMethod, Sale } from '../types'
import clsx from 'clsx'

function fmtCLP(n: number): string {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(n)
}

interface CartItem {
  product: Product
  quantity: number
}

export default function POSPage() {
  const [cart, setCart] = useState<CartItem[]>([])
  const [search, setSearch] = useState('')
  const [searchResults, setSearchResults] = useState<Product[]>([])
  const [showSearch, setShowSearch] = useState(false)
  const [paymentMethodId, setPaymentMethodId] = useState<number | null>(null)
  const [amountPaid, setAmountPaid] = useState('')
  const [customerRut, setCustomerRut] = useState('')
  const [customerName, setCustomerName] = useState('')
  const [emitDte, setEmitDte] = useState(false)
  const [lastSale, setLastSale] = useState<Sale | null>(null)
  const barcodeRef = useRef<HTMLInputElement>(null)

  const { data: paymentMethods } = useQuery<PaymentMethod[]>({
    queryKey: ['payment-methods'],
    queryFn: () => api.get('/sales/payment-methods').then(r => r.data),
  })

  const handleBarcodeInput = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const barcode = (e.target as HTMLInputElement).value.trim()
      if (!barcode) return
      try {
        const { data: product } = await api.get<Product>(`/products/barcode/${barcode}`)
        addToCart(product)
        ;(e.target as HTMLInputElement).value = ''
      } catch {
        toast.error(`Código ${barcode} no encontrado`)
      }
    }
  }

  const handleSearch = async (q: string) => {
    setSearch(q)
    if (q.length < 2) { setSearchResults([]); return }
    const { data } = await api.get(`/products?search=${q}&page_size=8`)
    setSearchResults(data.items)
    setShowSearch(true)
  }

  const addToCart = (product: Product) => {
    setCart(prev => {
      const existing = prev.find(i => i.product.id === product.id)
      if (existing) {
        return prev.map(i => i.product.id === product.id
          ? { ...i, quantity: i.quantity + 1 }
          : i
        )
      }
      return [...prev, { product, quantity: 1 }]
    })
    toast.success(`${product.name} agregado`)
  }

  const updateQty = (productId: number, qty: number) => {
    if (qty <= 0) {
      setCart(prev => prev.filter(i => i.product.id !== productId))
    } else {
      setCart(prev => prev.map(i => i.product.id === productId ? { ...i, quantity: qty } : i))
    }
  }

  const subtotal = cart.reduce((sum, item) => sum + Number(item.product.sale_price) * item.quantity, 0)
  const iva = cart.reduce((sum, item) => {
    if (!item.product.afecto_iva) return sum
    return sum + Number(item.product.sale_price) * item.quantity * 0.19
  }, 0)
  const total = subtotal + iva
  const change = amountPaid ? Number(amountPaid) - total : 0

  const saleMutation = useMutation({
    mutationFn: (data: any) => api.post('/sales', data),
    onSuccess: ({ data }: { data: Sale }) => {
      setLastSale(data)
      setCart([])
      setAmountPaid('')
      setCustomerRut('')
      setCustomerName('')
      toast.success('Venta registrada correctamente')
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || 'Error al registrar venta'),
  })

  const handleSell = () => {
    if (!cart.length) { toast.error('El carrito está vacío'); return }
    saleMutation.mutate({
      items: cart.map(i => ({ product_id: i.product.id, quantity: i.quantity })),
      payment_method_id: paymentMethodId,
      amount_paid: amountPaid ? Number(amountPaid) : null,
      customer_rut: customerRut || null,
      customer_name: customerName || null,
      emit_dte: emitDte,
    })
  }

  const downloadReceipt = (saleId: number) => {
    window.open(`/api/sales/${saleId}/receipt`, '_blank')
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Punto de Venta</h1>

      {lastSale && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="font-semibold text-green-800">Venta #{lastSale.id} registrada - Total: {fmtCLP(Number(lastSale.total))}</p>
            {lastSale.change_amount && Number(lastSale.change_amount) > 0 && (
              <p className="text-green-700 text-sm">Vuelto: {fmtCLP(Number(lastSale.change_amount))}</p>
            )}
          </div>
          <button className="btn-secondary" onClick={() => downloadReceipt(lastSale.id)}>
            <Printer size={16} /> Imprimir Boleta
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3 space-y-4">
          <div className="card">
            <div className="flex gap-3">
              <div className="relative flex-1">
                <Barcode size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-blue-500" />
                <input ref={barcodeRef} className="input pl-9 border-blue-300 focus:ring-blue-500"
                  placeholder="Escanear código de barras (Enter)..." onKeyDown={handleBarcodeInput} autoFocus />
              </div>
              <div className="relative flex-1">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input className="input pl-9" placeholder="Buscar producto..." value={search}
                  onChange={e => handleSearch(e.target.value)}
                  onBlur={() => setTimeout(() => setShowSearch(false), 200)} />
                {showSearch && searchResults.length > 0 && (
                  <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                    {searchResults.map(p => (
                      <button key={p.id} className="w-full text-left px-3 py-2 hover:bg-gray-50 flex items-center justify-between"
                        onClick={() => { addToCart(p); setSearch(''); setShowSearch(false) }}>
                        <div>
                          <span className="text-sm font-medium">{p.name}</span>
                          <span className="text-xs text-gray-400 ml-2">(Stock: {p.stock_current})</span>
                        </div>
                        <span className="text-sm font-medium text-primary-600">{fmtCLP(p.sale_price_with_iva)}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="card overflow-hidden p-0">
            <div className="px-4 py-3 bg-gray-50 border-b border-gray-100">
              <h3 className="font-semibold text-gray-900">Carrito ({cart.length} productos)</h3>
            </div>
            {cart.length === 0 ? (
              <div className="py-12 text-center text-gray-400">
                <ShoppingBag size={40} className="mx-auto mb-2 opacity-20" />
                <p>Agrega productos escaneando o buscando</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {cart.map(item => (
                  <div key={item.product.id} className="px-4 py-3 flex items-center gap-3">
                    <div className="flex-1">
                      <p className="font-medium text-sm text-gray-900">{item.product.name}</p>
                      <p className="text-xs text-gray-400">{fmtCLP(item.product.sale_price_with_iva)} c/u</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100"
                        onClick={() => updateQty(item.product.id, item.quantity - 1)}>
                        <Minus size={12} />
                      </button>
                      <span className="w-8 text-center font-medium">{item.quantity}</span>
                      <button className="w-7 h-7 rounded-full border border-gray-300 flex items-center justify-center hover:bg-gray-100"
                        onClick={() => updateQty(item.product.id, item.quantity + 1)}>
                        <Plus size={12} />
                      </button>
                    </div>
                    <p className="w-20 text-right font-medium text-sm">
                      {fmtCLP(Number(item.product.sale_price_with_iva) * item.quantity)}
                    </p>
                    <button className="text-red-400 hover:text-red-600" onClick={() => updateQty(item.product.id, 0)}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="card space-y-3">
            <h3 className="font-semibold text-gray-900">Resumen</h3>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between text-gray-600"><span>Subtotal (neto)</span><span>{fmtCLP(subtotal)}</span></div>
              <div className="flex justify-between text-gray-600"><span>IVA (19%)</span><span>{fmtCLP(iva)}</span></div>
              <div className="flex justify-between font-bold text-lg border-t pt-2"><span>TOTAL</span><span>{fmtCLP(total)}</span></div>
            </div>
          </div>

          <div className="card space-y-3">
            <h3 className="font-semibold text-gray-900">Pago</h3>
            <div>
              <label className="label">Método de Pago</label>
              <select className="input" value={paymentMethodId || ''} onChange={e => setPaymentMethodId(e.target.value ? Number(e.target.value) : null)}>
                <option value="">Seleccionar...</option>
                {paymentMethods?.map(pm => <option key={pm.id} value={pm.id}>{pm.name}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Monto Recibido (efectivo)</label>
              <input type="number" className="input" value={amountPaid}
                onChange={e => setAmountPaid(e.target.value)} placeholder="0" min="0" />
            </div>
            {change > 0 && (
              <div className="bg-green-50 rounded-lg p-3">
                <p className="text-sm font-medium text-green-700">Vuelto: {fmtCLP(change)}</p>
              </div>
            )}
            <div>
              <label className="label">RUT Cliente (opcional)</label>
              <input className="input" value={customerRut} onChange={e => setCustomerRut(e.target.value)} placeholder="12.345.678-9" />
            </div>
            <div className="flex items-center gap-2">
              <input type="checkbox" id="emit_dte" checked={emitDte} onChange={e => setEmitDte(e.target.checked)} />
              <label htmlFor="emit_dte" className="text-sm text-gray-700">Emitir boleta electrónica SII</label>
            </div>
          </div>

          <button
            className="btn-primary w-full py-4 text-lg"
            onClick={handleSell}
            disabled={cart.length === 0 || saleMutation.isPending}
          >
            {saleMutation.isPending ? 'Procesando...' : `Cobrar ${fmtCLP(total)}`}
          </button>
          <button className="btn-secondary w-full" onClick={() => setCart([])}>
            Limpiar Carrito
          </button>
        </div>
      </div>
    </div>
  )
}
