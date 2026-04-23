from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Integer, Text, ForeignKey, Enum, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class SaleStatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    COMPLETADA = "completada"
    ANULADA = "anulada"


class PaymentMethodType(str, enum.Enum):
    EFECTIVO = "efectivo"
    TARJETA_DEBITO = "tarjeta_debito"
    TARJETA_CREDITO = "tarjeta_credito"
    TRANSFERENCIA = "transferencia"
    OTRO = "otro"


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[PaymentMethodType] = mapped_column(Enum(PaymentMethodType), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sales: Mapped[list["Sale"]] = relationship("Sale", back_populates="payment_method")


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    folio: Mapped[int | None] = mapped_column(Integer, unique=True)
    status: Mapped[SaleStatus] = mapped_column(Enum(SaleStatus), default=SaleStatus.COMPLETADA)

    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    iva_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    payment_method_id: Mapped[int | None] = mapped_column(ForeignKey("payment_methods.id"))
    amount_paid: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    change_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))

    customer_rut: Mapped[str | None] = mapped_column(String(12))
    customer_name: Mapped[str | None] = mapped_column(String(200))

    dte_tipo: Mapped[str | None] = mapped_column(String(5))
    dte_folio: Mapped[int | None] = mapped_column(Integer)
    dte_fecha_emision: Mapped[datetime | None] = mapped_column(DateTime)
    dte_track_id: Mapped[str | None] = mapped_column(String(100))
    dte_xml_path: Mapped[str | None] = mapped_column(String(500))
    dte_pdf_path: Mapped[str | None] = mapped_column(String(500))
    dte_enviado: Mapped[bool] = mapped_column(Boolean, default=False)

    notes: Mapped[str | None] = mapped_column(Text)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)

    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    payment_method: Mapped["PaymentMethod | None"] = relationship("PaymentMethod", back_populates="sales")
    items: Mapped[list["SaleItem"]] = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price_with_iva: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    iva_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)

    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="sale_items")
