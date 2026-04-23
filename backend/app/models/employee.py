from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Date, Numeric, Integer, Text, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ContractType(str, enum.Enum):
    INDEFINIDO = "indefinido"
    PLAZO_FIJO = "plazo_fijo"
    HONORARIOS = "honorarios"


class VacationStatus(str, enum.Enum):
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    TOMADA = "tomada"


class AfpName(str, enum.Enum):
    CAPITAL = "Capital"
    CUPRUM = "Cuprum"
    HABITAT = "Habitat"
    MODELO = "Modelo"
    PLANVITAL = "PlanVital"
    PROVIDA = "ProVida"
    UNO = "Uno"


class IsapreName(str, enum.Enum):
    FONASA = "FONASA"
    BANMEDICA = "Banmédica"
    COLMENA = "Colmena"
    CONSALUD = "Consalud"
    CRUZ_BLANCA = "Cruz Blanca"
    ESENCIAL = "Esencial"
    MASVIDA = "Masvida"
    NUEVA_MASVIDA = "Nueva Masvida"
    VIDA_TRES = "Vida Tres"


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    rut: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(300))
    birth_date: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(10))
    nationality: Mapped[str] = mapped_column(String(50), default="Chilena")

    position: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100))

    afp: Mapped[AfpName | None] = mapped_column(Enum(AfpName))
    isapre: Mapped[IsapreName | None] = mapped_column(Enum(IsapreName))
    isapre_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    banco: Mapped[str | None] = mapped_column(String(100))
    cuenta_bancaria: Mapped[str | None] = mapped_column(String(50))
    tipo_cuenta: Mapped[str | None] = mapped_column(String(50))

    vacation_days_per_year: Mapped[int] = mapped_column(Integer, default=15)
    vacation_days_available: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="employee")
    salary_payments: Mapped[list["SalaryPayment"]] = relationship("SalaryPayment", back_populates="employee")
    vacation_requests: Mapped[list["VacationRequest"]] = relationship("VacationRequest", back_populates="employee")


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    contract_type: Mapped[ContractType] = mapped_column(Enum(ContractType), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gratificacion_legal: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="contracts")


class SalaryPayment(Base):
    __tablename__ = "salary_payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)

    sueldo_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    horas_extra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    valor_hora_extra: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    bono_colacion: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    bono_movilizacion: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    otros_haberes: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    gratificacion: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    total_haberes: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    afp_porcentaje: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0)
    afp_monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    sis_monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    isapre_monto: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    cesantia_trabajador: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    otros_descuentos: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)

    total_descuentos: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    liquido_pagar: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    pdf_path: Mapped[str | None] = mapped_column(String(500))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="salary_payments")


class VacationRequest(Base):
    __tablename__ = "vacation_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days_requested: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[VacationStatus] = mapped_column(Enum(VacationStatus), default=VacationStatus.PENDIENTE)
    reason: Mapped[str | None] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    employee: Mapped["Employee"] = relationship("Employee", back_populates="vacation_requests")
