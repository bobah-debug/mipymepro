from decimal import Decimal
from pydantic import BaseModel


class KPIResponse(BaseModel):
    period_year: int
    period_month: int
    total_ventas: Decimal
    total_ventas_prev: Decimal
    variacion_ventas_pct: float
    num_ventas: int
    ticket_promedio: Decimal
    total_gastos_sueldos: Decimal
    utilidad_bruta: Decimal
    margen_bruto_pct: float
    productos_bajo_stock: int


class DailySalesItem(BaseModel):
    date: str
    total: Decimal
    count: int


class TopProductItem(BaseModel):
    product_id: int
    product_name: str
    quantity_sold: int
    total: Decimal


class CategorySalesItem(BaseModel):
    category_name: str
    total: Decimal
    percentage: float


class DashboardResponse(BaseModel):
    kpis: KPIResponse
    daily_sales: list[DailySalesItem]
    top_products: list[TopProductItem]
    category_sales: list[CategorySalesItem]
