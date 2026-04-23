from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel
from app.models.employee import ContractType, VacationStatus, AfpName, IsapreName


class EmployeeCreate(BaseModel):
    rut: str
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    nationality: str = "Chilena"
    position: str
    department: str | None = None
    afp: AfpName | None = None
    isapre: IsapreName | None = None
    isapre_amount: Decimal | None = None
    banco: str | None = None
    cuenta_bancaria: str | None = None
    tipo_cuenta: str | None = None
    vacation_days_per_year: int = 15


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    birth_date: date | None = None
    position: str | None = None
    department: str | None = None
    afp: AfpName | None = None
    isapre: IsapreName | None = None
    isapre_amount: Decimal | None = None
    banco: str | None = None
    cuenta_bancaria: str | None = None
    tipo_cuenta: str | None = None
    vacation_days_per_year: int | None = None
    is_active: bool | None = None


class EmployeeResponse(BaseModel):
    id: int
    rut: str
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    position: str
    department: str | None
    afp: AfpName | None
    isapre: IsapreName | None
    isapre_amount: Decimal | None
    vacation_days_available: Decimal
    vacation_days_per_year: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    employee_id: int
    contract_type: ContractType
    start_date: date
    end_date: date | None = None
    base_salary: Decimal
    gratificacion_legal: bool = True
    notes: str | None = None


class ContractResponse(BaseModel):
    id: int
    employee_id: int
    contract_type: ContractType
    start_date: date
    end_date: date | None
    base_salary: Decimal
    gratificacion_legal: bool
    is_active: bool

    class Config:
        from_attributes = True


class SalaryPaymentCreate(BaseModel):
    employee_id: int
    period_year: int
    period_month: int
    sueldo_base: Decimal
    horas_extra: Decimal = Decimal("0")
    valor_hora_extra: Decimal = Decimal("0")
    bono_colacion: Decimal = Decimal("0")
    bono_movilizacion: Decimal = Decimal("0")
    otros_haberes: Decimal = Decimal("0")
    otros_descuentos: Decimal = Decimal("0")


class SalaryPaymentResponse(BaseModel):
    id: int
    employee_id: int
    period_year: int
    period_month: int
    sueldo_base: Decimal
    gratificacion: Decimal
    total_haberes: Decimal
    afp_porcentaje: Decimal
    afp_monto: Decimal
    sis_monto: Decimal
    isapre_monto: Decimal
    cesantia_trabajador: Decimal
    total_descuentos: Decimal
    liquido_pagar: Decimal
    pdf_path: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class VacationRequestCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: str | None = None


class VacationRequestUpdate(BaseModel):
    status: VacationStatus
    rejection_reason: str | None = None


class VacationRequestResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    days_requested: int
    status: VacationStatus
    reason: str | None
    rejection_reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True
