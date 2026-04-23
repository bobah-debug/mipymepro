from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.product import MovementType


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool

    class Config:
        from_attributes = True


class SupplierCreate(BaseModel):
    rut: str | None = None
    name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class SupplierUpdate(BaseModel):
    rut: str | None = None
    name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None


class SupplierResponse(BaseModel):
    id: int
    rut: str | None
    name: str
    contact_name: str | None
    email: str | None
    phone: str | None
    is_active: bool

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    code: str
    barcode: str | None = None
    name: str
    description: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    purchase_price: Decimal = Decimal("0")
    sale_price: Decimal
    stock_minimum: int = 0
    stock_maximum: int | None = None
    unit: str = "unidad"
    afecto_iva: bool = True


class ProductUpdate(BaseModel):
    code: str | None = None
    barcode: str | None = None
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    purchase_price: Decimal | None = None
    sale_price: Decimal | None = None
    stock_minimum: int | None = None
    stock_maximum: int | None = None
    unit: str | None = None
    afecto_iva: bool | None = None
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    code: str
    barcode: str | None
    name: str
    description: str | None
    category_id: int | None
    category: CategoryResponse | None
    supplier_id: int | None
    purchase_price: Decimal
    sale_price: Decimal
    sale_price_with_iva: Decimal
    stock_current: int
    stock_minimum: int
    unit: str
    afecto_iva: bool
    is_active: bool
    barcode_image_path: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: MovementType
    quantity: int
    unit_cost: Decimal | None = None
    reference: str | None = None
    notes: str | None = None
    supplier_id: int | None = None


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: MovementType
    quantity: int
    stock_before: int
    stock_after: int
    unit_cost: Decimal | None
    reference: str | None
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int
