from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.company import Company
from app.utils.deps import get_current_user
from app.models.user import User
import os, shutil
from app.config import settings

router = APIRouter(prefix="/company", tags=["Empresa"])


class CompanyUpdate(BaseModel):
    rut: str | None = None
    razon_social: str | None = None
    nombre_fantasia: str | None = None
    giro: str | None = None
    direccion: str | None = None
    comuna: str | None = None
    ciudad: str | None = None
    telefono: str | None = None
    email: str | None = None
    sii_ambiente: str | None = None
    sii_resolucion_numero: str | None = None
    sii_resolucion_fecha: str | None = None
    iva_porcentaje: int | None = None
    notas_boleta: str | None = None


@router.get("")
def get_company(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    company = db.query(Company).first()
    if not company:
        return {}
    return company


@router.put("")
def update_company(data: CompanyUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    company = db.query(Company).first()
    if not company:
        company = Company()
        db.add(company)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(company, k, v)
    db.commit()
    db.refresh(company)
    return company


@router.post("/logo")
def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logo_path = os.path.join(settings.UPLOAD_DIR, f"logo_{file.filename}")
    with open(logo_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    company = db.query(Company).first()
    if company:
        company.logo_path = logo_path
        db.commit()
    return {"logo_path": logo_path}


@router.post("/sii-cert")
def upload_sii_cert(
    file: UploadFile = File(...),
    password: str = "",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    cert_path = os.path.join(settings.UPLOAD_DIR, "sii_cert.p12")
    with open(cert_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    company = db.query(Company).first()
    if company:
        company.sii_cert_path = cert_path
        if password:
            company.sii_cert_password = password
        db.commit()
    return {"message": "Certificado cargado correctamente"}
