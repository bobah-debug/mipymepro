from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Category, Supplier
from app.schemas.product import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse,
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse,
    StockMovementCreate, StockMovementResponse,
)
from app.services import product_service
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Inventario"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Category).filter(Category.is_active == True).order_by(Category.name).all()


@router.post("/categories", response_model=CategoryResponse)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/categories/{cat_id}", response_model=CategoryResponse)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(cat, k, v)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Supplier).filter(Supplier.is_active == True).order_by(Supplier.name).all()


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/suppliers/{sup_id}", response_model=SupplierResponse)
def update_supplier(sup_id: int, data: SupplierUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    supplier = db.query(Supplier).filter(Supplier.id == sup_id).first()
    if not supplier:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(supplier, k, v)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category_id: int | None = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return product_service.get_products(db, page, page_size, search, category_id, low_stock)


@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_by_barcode(barcode: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return product_service.get_product_by_barcode(db, barcode)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from fastapi import HTTPException
    from app.models.product import Product
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return p


@router.post("", response_model=ProductResponse)
def create_product(data: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return product_service.create_product(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return product_service.update_product(db, product_id, data)


@router.post("/stock-movements", response_model=StockMovementResponse)
def create_movement(data: StockMovementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return product_service.create_stock_movement(db, data, current_user.id)


@router.get("/{product_id}/movements", response_model=list[StockMovementResponse])
def get_movements(product_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.product import StockMovement
    return db.query(StockMovement).filter(StockMovement.product_id == product_id).order_by(StockMovement.created_at.desc()).all()
