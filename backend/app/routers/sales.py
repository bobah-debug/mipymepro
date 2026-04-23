from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse, SaleListResponse, PaymentMethodCreate, PaymentMethodResponse
from app.services import sale_service
from app.services.pdf_service import generate_sale_receipt_pdf
from app.models.sale import PaymentMethod, SaleStatus
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/sales", tags=["Ventas"])


@router.get("/payment-methods", response_model=list[PaymentMethodResponse])
def list_payment_methods(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(PaymentMethod).filter(PaymentMethod.is_active == True).all()


@router.post("/payment-methods", response_model=PaymentMethodResponse)
def create_payment_method(data: PaymentMethodCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    pm = PaymentMethod(**data.model_dump())
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


@router.get("", response_model=SaleListResponse)
def list_sales(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    year: int | None = None,
    month: int | None = None,
    status: SaleStatus | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return sale_service.get_sales(db, page, page_size, year, month, status)


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from fastapi import HTTPException
    from app.models.sale import Sale
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return sale


@router.post("", response_model=SaleResponse)
def create_sale(data: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return sale_service.create_sale(db, data, current_user.id)


@router.post("/{sale_id}/cancel")
def cancel_sale(
    sale_id: int,
    reason: str = Query(..., description="Motivo de anulación"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sale = sale_service.cancel_sale(db, sale_id, reason, current_user.id)
    return {"message": "Venta anulada correctamente", "sale_id": sale.id}


@router.get("/{sale_id}/receipt")
def download_receipt(sale_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from fastapi import HTTPException
    from app.models.sale import Sale
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    pdf_path = generate_sale_receipt_pdf(db, sale)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"boleta_{sale_id}.pdf")
