from datetime import datetime
from sqlalchemy import String, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True)
    rut: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    razon_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_fantasia: Mapped[str | None] = mapped_column(String(200))
    giro: Mapped[str | None] = mapped_column(String(200))
    direccion: Mapped[str | None] = mapped_column(String(300))
    comuna: Mapped[str | None] = mapped_column(String(100))
    ciudad: Mapped[str | None] = mapped_column(String(100))
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    logo_path: Mapped[str | None] = mapped_column(String(500))

    sii_ambiente: Mapped[str] = mapped_column(String(20), default="certificacion")
    sii_cert_path: Mapped[str | None] = mapped_column(String(500))
    sii_cert_password: Mapped[str | None] = mapped_column(String(255))
    sii_resolucion_numero: Mapped[str | None] = mapped_column(String(20))
    sii_resolucion_fecha: Mapped[str | None] = mapped_column(String(20))

    iva_porcentaje: Mapped[int] = mapped_column(default=19)

    notas_boleta: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
