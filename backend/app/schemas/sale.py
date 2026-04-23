from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.sale import SaleStatus, PaymentMethodType


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    discount_pct: Decimal = Decimal("0")


class SaleCreate(BaseModel):
    items: list[SaleItemCreate]
    payment_method_id: int | None = None
    amount_paid: Decimal | None = None
    customer_rut: str | None = None
    customer_name: str | None = None
    notes: str | None = None
    emit_dte: bool = False


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str | None = None
    quantity: int
    unit_price: Decimal
    unit_price_with_iva: Decimal
    subtotal: Decimal
    iva_amount: Decimal
    total: Decimal
    discount_pct: Decimal

    class Config:
        from_attributes = True


class SaleResponse(BaseModel):
    id: int
    folio: int | None
    status: SaleStatus
    subtotal: Decimal
    iva_amount: Decimal
    total: Decimal
    payment_method_id: int | None
    amount_paid: Decimal | None
    change_amount: Decimal | None
    customer_rut: str | None
    customer_name: str | None
    dte_folio: int | None
    dte_enviado: bool
    dte_pdf_path: str | None
    items: list[SaleItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    items: list[SaleResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaymentMethodCreate(BaseModel):
    name: str
    type: PaymentMethodType


class PaymentMethodResponse(BaseModel):
    id: int
    name: str
    type: PaymentMethodType
    is_active: bool

    class Config:
        from_attributes = True
