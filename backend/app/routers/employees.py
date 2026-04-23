from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    ContractCreate, ContractResponse,
    SalaryPaymentCreate, SalaryPaymentResponse,
    VacationRequestCreate, VacationRequestUpdate, VacationRequestResponse,
)
from app.services import employee_service
from app.models.employee import VacationRequest
from app.utils.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/employees", tags=["RRHH"])


@router.get("", response_model=list[EmployeeResponse])
def list_employees(active_only: bool = True, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.get_employees(db, active_only)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.get_employee(db, employee_id)


@router.post("", response_model=EmployeeResponse)
def create_employee(data: EmployeeCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.create_employee(db, data)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.update_employee(db, employee_id, data)


@router.post("/contracts", response_model=ContractResponse)
def create_contract(data: ContractCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.create_contract(db, data)


@router.get("/{employee_id}/contracts", response_model=list[ContractResponse])
def get_contracts(employee_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.employee import Contract
    return db.query(Contract).filter(Contract.employee_id == employee_id).order_by(Contract.start_date.desc()).all()


@router.post("/salary-payments", response_model=SalaryPaymentResponse)
def create_salary_payment(data: SalaryPaymentCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.calculate_salary(db, data)


@router.get("/{employee_id}/salary-payments", response_model=list[SalaryPaymentResponse])
def get_salary_payments(employee_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.employee import SalaryPayment
    return db.query(SalaryPayment).filter(SalaryPayment.employee_id == employee_id).order_by(
        SalaryPayment.period_year.desc(), SalaryPayment.period_month.desc()
    ).all()


@router.get("/salary-payments/{payment_id}/pdf")
def download_liquidacion(payment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    from fastapi import HTTPException
    from app.models.employee import SalaryPayment
    payment = db.query(SalaryPayment).filter(SalaryPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")
    if not payment.pdf_path:
        from app.services.pdf_service import generate_liquidacion_pdf
        payment.pdf_path = generate_liquidacion_pdf(db, payment)
        db.commit()
    return FileResponse(payment.pdf_path, media_type="application/pdf",
                        filename=f"liquidacion_{payment_id}.pdf")


@router.get("/vacation-requests", response_model=list[VacationRequestResponse])
def list_vacation_requests(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(VacationRequest).order_by(VacationRequest.created_at.desc()).all()


@router.post("/vacation-requests", response_model=VacationRequestResponse)
def create_vacation_request(data: VacationRequestCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return employee_service.request_vacation(db, data)


@router.put("/vacation-requests/{request_id}", response_model=VacationRequestResponse)
def update_vacation_request(
    request_id: int,
    data: VacationRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return employee_service.update_vacation(db, request_id, data, current_user.id)
