export interface User {
  id: number
  email: string
  username: string
  full_name: string
  is_active: boolean
  role: 'admin' | 'vendedor' | 'rrhh' | 'contador'
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

export interface Product {
  id: number
  code: string
  barcode: string | null
  name: string
  description: string | null
  category_id: number | null
  category: Category | null
  supplier_id: number | null
  purchase_price: number
  sale_price: number
  sale_price_with_iva: number
  stock_current: number
  stock_minimum: number
  unit: string
  afecto_iva: boolean
  is_active: boolean
  barcode_image_path: string | null
  created_at: string
}

export interface Category {
  id: number
  name: string
  description: string | null
  is_active: boolean
}

export interface Supplier {
  id: number
  rut: string | null
  name: string
  contact_name: string | null
  email: string | null
  phone: string | null
  is_active: boolean
}

export interface StockMovement {
  id: number
  product_id: number
  movement_type: 'entrada' | 'salida' | 'ajuste' | 'devolucion'
  quantity: number
  stock_before: number
  stock_after: number
  unit_cost: number | null
  reference: string | null
  notes: string | null
  created_at: string
}

export interface Sale {
  id: number
  folio: number | null
  status: 'pendiente' | 'completada' | 'anulada'
  subtotal: number
  iva_amount: number
  total: number
  payment_method_id: number | null
  amount_paid: number | null
  change_amount: number | null
  customer_rut: string | null
  customer_name: string | null
  dte_folio: number | null
  dte_enviado: boolean
  dte_pdf_path: string | null
  items: SaleItem[]
  created_at: string
}

export interface SaleItem {
  id: number
  product_id: number
  product_name: string | null
  quantity: number
  unit_price: number
  unit_price_with_iva: number
  subtotal: number
  iva_amount: number
  total: number
  discount_pct: number
}

export interface PaymentMethod {
  id: number
  name: string
  type: string
  is_active: boolean
}

export interface Employee {
  id: number
  rut: string
  first_name: string
  last_name: string
  email: string | null
  phone: string | null
  position: string
  department: string | null
  afp: string | null
  isapre: string | null
  isapre_amount: number | null
  vacation_days_available: number
  vacation_days_per_year: number
  is_active: boolean
  created_at: string
}

export interface Contract {
  id: number
  employee_id: number
  contract_type: string
  start_date: string
  end_date: string | null
  base_salary: number
  gratificacion_legal: boolean
  is_active: boolean
}

export interface SalaryPayment {
  id: number
  employee_id: number
  period_year: number
  period_month: number
  sueldo_base: number
  gratificacion: number
  total_haberes: number
  afp_porcentaje: number
  afp_monto: number
  sis_monto: number
  isapre_monto: number
  cesantia_trabajador: number
  total_descuentos: number
  liquido_pagar: number
  pdf_path: string | null
  created_at: string
}

export interface VacationRequest {
  id: number
  employee_id: number
  start_date: string
  end_date: string
  days_requested: number
  status: 'pendiente' | 'aprobada' | 'rechazada' | 'tomada'
  reason: string | null
  rejection_reason: string | null
  created_at: string
}

export interface DashboardKPI {
  period_year: number
  period_month: number
  total_ventas: number
  total_ventas_prev: number
  variacion_ventas_pct: number
  num_ventas: number
  ticket_promedio: number
  total_gastos_sueldos: number
  utilidad_bruta: number
  margen_bruto_pct: number
  productos_bajo_stock: number
}

export interface DashboardData {
  kpis: DashboardKPI
  daily_sales: Array<{ date: string; total: number; count: number }>
  top_products: Array<{ product_id: number; product_name: string; quantity_sold: number; total: number }>
  category_sales: Array<{ category_name: string; total: number; percentage: number }>
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface Company {
  id?: number
  rut: string
  razon_social: string
  nombre_fantasia?: string
  giro?: string
  direccion?: string
  comuna?: string
  ciudad?: string
  telefono?: string
  email?: string
  sii_ambiente: string
  sii_resolucion_numero?: string
  iva_porcentaje: number
  notas_boleta?: string
}
