from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.sale import Sale, SaleItem, SaleStatus, PaymentMethod
from app.models.product import Product, StockMovement, MovementType
from app.schemas.sale import SaleCreate
from app.config import settings


IVA = Decimal("0.19")


def create_sale(db: Session, data: SaleCreate, created_by: int | None = None) -> Sale:
    if not data.items:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un producto")

    subtotal = Decimal("0")
    iva_total = Decimal("0")
    sale_items = []

    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id, Product.is_active == True).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Producto {item_data.product_id} no encontrado")
        if product.stock_current < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

        discount = item_data.discount_pct / 100
        unit_price = product.sale_price * (1 - discount)
        unit_price_with_iva = product.sale_price_with_iva * (1 - discount)
        item_subtotal = (unit_price * item_data.quantity).quantize(Decimal("1"))
        item_iva = (item_subtotal * IVA).quantize(Decimal("1")) if product.afecto_iva else Decimal("0")
        item_total = item_subtotal + item_iva

        subtotal += item_subtotal
        iva_total += item_iva

        sale_items.append(SaleItem(
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=unit_price,
            unit_price_with_iva=unit_price_with_iva,
            subtotal=item_subtotal,
            iva_amount=item_iva,
            total=item_total,
            discount_pct=item_data.discount_pct,
        ))

    total = subtotal + iva_total
    change = None
    if data.amount_paid is not None:
        change = data.amount_paid - total

    sale = Sale(
        subtotal=subtotal,
        iva_amount=iva_total,
        total=total,
        payment_method_id=data.payment_method_id,
        amount_paid=data.amount_paid,
        change_amount=change,
        customer_rut=data.customer_rut,
        customer_name=data.customer_name,
        notes=data.notes,
        created_by=created_by,
        status=SaleStatus.COMPLETADA,
    )
    db.add(sale)
    db.flush()

    for item in sale_items:
        item.sale_id = sale.id
        db.add(item)

        product = db.query(Product).filter(Product.id == item.product_id).first()
        stock_before = product.stock_current
        product.stock_current -= item.quantity
        movement = StockMovement(
            product_id=item.product_id,
            movement_type=MovementType.SALIDA,
            quantity=item.quantity,
            stock_before=stock_before,
            stock_after=product.stock_current,
            sale_id=sale.id,
            created_by=created_by,
        )
        db.add(movement)

    db.commit()
    db.refresh(sale)

    if data.emit_dte:
        _emit_dte(db, sale)

    return sale


def cancel_sale(db: Session, sale_id: int, reason: str, user_id: int | None = None) -> Sale:
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if sale.status == SaleStatus.ANULADA:
        raise HTTPException(status_code=400, detail="La venta ya está anulada")

    sale.status = SaleStatus.ANULADA
    sale.cancellation_reason = reason

    for item in sale.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            stock_before = product.stock_current
            product.stock_current += item.quantity
            movement = StockMovement(
                product_id=item.product_id,
                movement_type=MovementType.DEVOLUCION,
                quantity=item.quantity,
                stock_before=stock_before,
                stock_after=product.stock_current,
                sale_id=sale.id,
                reference=f"Anulación venta #{sale.id}",
                created_by=user_id,
            )
            db.add(movement)

    db.commit()
    db.refresh(sale)
    return sale


def get_sales(db: Session, page: int = 1, page_size: int = 20, year: int | None = None,
              month: int | None = None, status: SaleStatus | None = None):
    from sqlalchemy import extract
    query = db.query(Sale)
    if year:
        query = query.filter(extract("year", Sale.created_at) == year)
    if month:
        query = query.filter(extract("month", Sale.created_at) == month)
    if status:
        query = query.filter(Sale.status == status)
    total = query.count()
    items = query.order_by(Sale.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size
    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}


def _emit_dte(db: Session, sale: Sale):
    from app.services.sii_service import emit_boleta
    try:
        emit_boleta(db, sale)
    except Exception as e:
        pass
