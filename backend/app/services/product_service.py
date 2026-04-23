import os
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from app.models.product import Product, Category, Supplier, StockMovement, MovementType
from app.models.company import Company
from app.schemas.product import ProductCreate, ProductUpdate, StockMovementCreate
from app.config import settings


IVA = Decimal("0.19")


def _calc_price_with_iva(price: Decimal, afecto: bool) -> Decimal:
    if afecto:
        return (price * (1 + IVA)).quantize(Decimal("1"))
    return price


def get_products(db: Session, page: int = 1, page_size: int = 20, search: str | None = None,
                 category_id: int | None = None, low_stock: bool = False, active_only: bool = True):
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)
    if search:
        query = query.filter(
            or_(Product.name.ilike(f"%{search}%"), Product.code.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%"))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if low_stock:
        query = query.filter(Product.stock_current <= Product.stock_minimum)
    total = query.count()
    items = query.order_by(Product.name).offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size
    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}


def get_product_by_barcode(db: Session, barcode: str) -> Product:
    product = db.query(Product).filter(Product.barcode == barcode, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto con código {barcode} no encontrado")
    return product


def create_product(db: Session, data: ProductCreate) -> Product:
    existing = db.query(Product).filter(Product.code == data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")

    price_with_iva = _calc_price_with_iva(data.sale_price, data.afecto_iva)
    product = Product(
        **data.model_dump(exclude={"sale_price"}),
        sale_price=data.sale_price,
        sale_price_with_iva=price_with_iva,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    _generate_barcode_image(product)
    db.commit()
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    update_data = data.model_dump(exclude_none=True)
    if "sale_price" in update_data:
        afecto = update_data.get("afecto_iva", product.afecto_iva)
        update_data["sale_price_with_iva"] = _calc_price_with_iva(update_data["sale_price"], afecto)
    for key, val in update_data.items():
        setattr(product, key, val)
    db.commit()
    db.refresh(product)
    return product


def create_stock_movement(db: Session, data: StockMovementCreate, created_by: int | None = None) -> StockMovement:
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    stock_before = product.stock_current
    if data.movement_type == MovementType.ENTRADA:
        product.stock_current += data.quantity
    elif data.movement_type == MovementType.SALIDA:
        if product.stock_current < data.quantity:
            raise HTTPException(status_code=400, detail="Stock insuficiente")
        product.stock_current -= data.quantity
    elif data.movement_type == MovementType.AJUSTE:
        product.stock_current = data.quantity
    elif data.movement_type == MovementType.DEVOLUCION:
        product.stock_current += data.quantity

    movement = StockMovement(
        product_id=data.product_id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        stock_before=stock_before,
        stock_after=product.stock_current,
        unit_cost=data.unit_cost,
        reference=data.reference,
        notes=data.notes,
        supplier_id=data.supplier_id,
        created_by=created_by,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def _generate_barcode_image(product: Product):
    if not product.barcode:
        return
    try:
        import barcode
        from barcode.writer import ImageWriter
        import io

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        EAN = barcode.get_barcode_class("code128")
        ean = EAN(product.barcode, writer=ImageWriter())
        filepath = os.path.join(settings.UPLOAD_DIR, f"barcode_{product.id}")
        ean.save(filepath)
        product.barcode_image_path = filepath + ".png"
    except Exception:
        pass
