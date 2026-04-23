from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.product import Product, Category
from app.models.employee import SalaryPayment
from app.schemas.dashboard import (
    KPIResponse, DailySalesItem, TopProductItem, CategorySalesItem, DashboardResponse
)


def get_dashboard(db: Session, year: int, month: int) -> DashboardResponse:
    kpis = _calc_kpis(db, year, month)
    daily = _daily_sales(db, year, month)
    top_prods = _top_products(db, year, month)
    cat_sales = _category_sales(db, year, month)
    return DashboardResponse(kpis=kpis, daily_sales=daily, top_products=top_prods, category_sales=cat_sales)


def _calc_kpis(db: Session, year: int, month: int) -> KPIResponse:
    def sales_sum(y, m):
        result = db.query(func.sum(Sale.total)).filter(
            extract("year", Sale.created_at) == y,
            extract("month", Sale.created_at) == m,
            Sale.status == SaleStatus.COMPLETADA,
        ).scalar()
        return result or Decimal("0")

    def sales_count(y, m):
        return db.query(func.count(Sale.id)).filter(
            extract("year", Sale.created_at) == y,
            extract("month", Sale.created_at) == m,
            Sale.status == SaleStatus.COMPLETADA,
        ).scalar() or 0

    total = sales_sum(year, month)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    total_prev = sales_sum(prev_year, prev_month)

    variacion = float(((total - total_prev) / total_prev * 100) if total_prev else 0)
    num = sales_count(year, month)
    ticket = (total / num).quantize(Decimal("1")) if num else Decimal("0")

    gastos_sueldos = db.query(func.sum(SalaryPayment.liquido_pagar)).filter(
        SalaryPayment.period_year == year,
        SalaryPayment.period_month == month,
    ).scalar() or Decimal("0")

    from app.models.product import Product
    bajo_stock = db.query(func.count(Product.id)).filter(
        Product.stock_current <= Product.stock_minimum,
        Product.is_active == True,
    ).scalar() or 0

    utilidad = total - gastos_sueldos
    margen = float((utilidad / total * 100) if total else 0)

    return KPIResponse(
        period_year=year, period_month=month,
        total_ventas=total, total_ventas_prev=total_prev,
        variacion_ventas_pct=round(variacion, 2),
        num_ventas=num, ticket_promedio=ticket,
        total_gastos_sueldos=gastos_sueldos,
        utilidad_bruta=utilidad,
        margen_bruto_pct=round(margen, 2),
        productos_bajo_stock=bajo_stock,
    )


def _daily_sales(db: Session, year: int, month: int) -> list[DailySalesItem]:
    rows = db.query(
        func.date(Sale.created_at).label("date"),
        func.sum(Sale.total).label("total"),
        func.count(Sale.id).label("count"),
    ).filter(
        extract("year", Sale.created_at) == year,
        extract("month", Sale.created_at) == month,
        Sale.status == SaleStatus.COMPLETADA,
    ).group_by(func.date(Sale.created_at)).order_by("date").all()

    return [DailySalesItem(date=str(r.date), total=r.total or 0, count=r.count) for r in rows]


def _top_products(db: Session, year: int, month: int, limit: int = 10) -> list[TopProductItem]:
    rows = db.query(
        SaleItem.product_id,
        Product.name,
        func.sum(SaleItem.quantity).label("qty"),
        func.sum(SaleItem.total).label("total"),
    ).join(Product, Product.id == SaleItem.product_id).join(Sale, Sale.id == SaleItem.sale_id).filter(
        extract("year", Sale.created_at) == year,
        extract("month", Sale.created_at) == month,
        Sale.status == SaleStatus.COMPLETADA,
    ).group_by(SaleItem.product_id, Product.name).order_by(func.sum(SaleItem.total).desc()).limit(limit).all()

    return [TopProductItem(product_id=r.product_id, product_name=r.name,
                           quantity_sold=r.qty or 0, total=r.total or 0) for r in rows]


def _category_sales(db: Session, year: int, month: int) -> list[CategorySalesItem]:
    rows = db.query(
        Category.name,
        func.sum(SaleItem.total).label("total"),
    ).join(Product, Product.category_id == Category.id).join(
        SaleItem, SaleItem.product_id == Product.id
    ).join(Sale, Sale.id == SaleItem.sale_id).filter(
        extract("year", Sale.created_at) == year,
        extract("month", Sale.created_at) == month,
        Sale.status == SaleStatus.COMPLETADA,
    ).group_by(Category.name).all()

    grand_total = sum(r.total or 0 for r in rows) or Decimal("1")
    return [
        CategorySalesItem(
            category_name=r.name,
            total=r.total or 0,
            percentage=round(float((r.total or 0) / grand_total * 100), 2)
        ) for r in rows
    ]
