from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.employee import Employee, Contract, SalaryPayment, VacationRequest, VacationStatus
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, ContractCreate,
    SalaryPaymentCreate, VacationRequestCreate, VacationRequestUpdate
)


AFP_RATES = {
    "Capital": Decimal("0.1145"),
    "Cuprum": Decimal("0.1148"),
    "Habitat": Decimal("0.1127"),
    "Modelo": Decimal("0.1058"),
    "PlanVital": Decimal("0.1116"),
    "ProVida": Decimal("0.1145"),
    "Uno": Decimal("0.1069"),
}
SIS_RATE = Decimal("0.0087")
CESANTIA_TRABAJADOR_RATE = Decimal("0.006")
GRATIFICACION_TOPE_ANUAL = Decimal("4_75476")
GRATIFICACION_PCT = Decimal("0.25")


def get_employees(db: Session, active_only: bool = True):
    query = db.query(Employee)
    if active_only:
        query = query.filter(Employee.is_active == True)
    return query.order_by(Employee.last_name, Employee.first_name).all()


def get_employee(db: Session, employee_id: int) -> Employee:
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return emp


def create_employee(db: Session, data: EmployeeCreate) -> Employee:
    existing = db.query(Employee).filter(Employee.rut == data.rut).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese RUT")
    emp = Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> Employee:
    emp = get_employee(db, employee_id)
    for key, val in data.model_dump(exclude_none=True).items():
        setattr(emp, key, val)
    db.commit()
    db.refresh(emp)
    return emp


def create_contract(db: Session, data: ContractCreate) -> Contract:
    db.query(Contract).filter(
        Contract.employee_id == data.employee_id,
        Contract.is_active == True
    ).update({"is_active": False})
    contract = Contract(**data.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


def calculate_salary(db: Session, data: SalaryPaymentCreate) -> SalaryPayment:
    emp = get_employee(db, data.employee_id)

    existing = db.query(SalaryPayment).filter(
        SalaryPayment.employee_id == data.employee_id,
        SalaryPayment.period_year == data.period_year,
        SalaryPayment.period_month == data.period_month,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una liquidación para este período")

    horas_extra_total = data.horas_extra * data.valor_hora_extra
    gratificacion = (data.sueldo_base * GRATIFICACION_PCT / 12).quantize(Decimal("1"))
    total_haberes = (
        data.sueldo_base + horas_extra_total + data.bono_colacion +
        data.bono_movilizacion + data.otros_haberes + gratificacion
    ).quantize(Decimal("1"))

    afp_rate = AFP_RATES.get(emp.afp.value if emp.afp else "", Decimal("0.1145"))
    imponible = (data.sueldo_base + horas_extra_total + gratificacion).quantize(Decimal("1"))
    afp_monto = (imponible * afp_rate).quantize(Decimal("1"))
    sis_monto = (imponible * SIS_RATE).quantize(Decimal("1"))
    isapre_monto = emp.isapre_amount or Decimal("0")
    cesantia = (imponible * CESANTIA_TRABAJADOR_RATE).quantize(Decimal("1"))

    total_descuentos = (afp_monto + sis_monto + isapre_monto + cesantia + data.otros_descuentos).quantize(Decimal("1"))
    liquido = (total_haberes - total_descuentos).quantize(Decimal("1"))

    payment = SalaryPayment(
        employee_id=data.employee_id,
        period_year=data.period_year,
        period_month=data.period_month,
        sueldo_base=data.sueldo_base,
        horas_extra=data.horas_extra,
        valor_hora_extra=data.valor_hora_extra,
        bono_colacion=data.bono_colacion,
        bono_movilizacion=data.bono_movilizacion,
        otros_haberes=data.otros_haberes,
        gratificacion=gratificacion,
        total_haberes=total_haberes,
        afp_porcentaje=afp_rate,
        afp_monto=afp_monto,
        sis_monto=sis_monto,
        isapre_monto=isapre_monto,
        cesantia_trabajador=cesantia,
        otros_descuentos=data.otros_descuentos,
        total_descuentos=total_descuentos,
        liquido_pagar=liquido,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    from app.services.pdf_service import generate_liquidacion_pdf
    pdf_path = generate_liquidacion_pdf(db, payment)
    payment.pdf_path = pdf_path
    db.commit()

    return payment


def request_vacation(db: Session, data: VacationRequestCreate) -> VacationRequest:
    emp = get_employee(db, data.employee_id)
    days = (data.end_date - data.start_date).days + 1
    if emp.vacation_days_available < days:
        raise HTTPException(status_code=400, detail=f"Días disponibles insuficientes ({emp.vacation_days_available})")

    req = VacationRequest(
        employee_id=data.employee_id,
        start_date=data.start_date,
        end_date=data.end_date,
        days_requested=days,
        reason=data.reason,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def update_vacation(db: Session, request_id: int, data: VacationRequestUpdate, approver_id: int | None = None) -> VacationRequest:
    req = db.query(VacationRequest).filter(VacationRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    req.status = data.status
    req.rejection_reason = data.rejection_reason
    req.approved_by = approver_id

    if data.status == VacationStatus.APROBADA:
        emp = get_employee(db, req.employee_id)
        emp.vacation_days_available -= req.days_requested

    db.commit()
    db.refresh(req)
    return req
