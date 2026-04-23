from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Numeric, Integer, Text, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class MovementType(str, enum.Enum):
    ENTRADA = "entrada"
    SALIDA = "salida"
    AJUSTE = "ajuste"
    DEVOLUCION = "devolucion"


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    rut: Mapped[str | None] = mapped_column(String(12))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    products: Mapped[list["Product"]] = relationship("Product", back_populates="supplier")
    stock_movements: Mapped[list["StockMovement"]] = relationship("StockMovement", back_populates="supplier")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))

    purchase_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sale_price_with_iva: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    stock_current: Mapped[int] = mapped_column(Integer, default=0)
    stock_minimum: Mapped[int] = mapped_column(Integer, default=0)
    stock_maximum: Mapped[int | None] = mapped_column(Integer)

    unit: Mapped[str] = mapped_column(String(20), default="unidad")
    image_path: Mapped[str | None] = mapped_column(String(500))
    barcode_image_path: Mapped[str | None] = mapped_column(String(500))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    afecto_iva: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    category: Mapped["Category | None"] = relationship("Category", back_populates="products")
    supplier: Mapped["Supplier | None"] = relationship("Supplier", back_populates="products")
    stock_movements: Mapped[list["StockMovement"]] = relationship("StockMovement", back_populates="product")
    sale_items: Mapped[list["SaleItem"]] = relationship("SaleItem", back_populates="product")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_before: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_after: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    reference: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id"))
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship("Product", back_populates="stock_movements")
    supplier: Mapped["Supplier | None"] = relationship("Supplier", back_populates="stock_movements")


from app.models.sale import SaleItem, Sale  # noqa: E402 - evitar circular imports
