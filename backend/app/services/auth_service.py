from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.config import settings
from app.models.user import User, Role, RoleName
from app.models.sale import PaymentMethod, PaymentMethodType
from app.models.product import Category


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario desactivado")
    return user


def get_or_create_role(db: Session, role_name: RoleName) -> Role:
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        role = Role(name=role_name, description=role_name.value.capitalize())
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def seed_initial_data(db: Session):
    for role_name in RoleName:
        get_or_create_role(db, role_name)

    admin_role = get_or_create_role(db, RoleName.ADMIN)
    existing = db.query(User).filter(User.username == "admin").first()
    if not existing:
        admin = User(
            email="admin@empresa.cl",
            username="admin",
            full_name="Administrador",
            hashed_password=hash_password("admin1234"),
            role_id=admin_role.id,
            is_active=True,
        )
        db.add(admin)
        db.commit()

    payment_methods_seed = [
        {"name": "Efectivo", "type": PaymentMethodType.EFECTIVO},
        {"name": "Tarjeta de Débito", "type": PaymentMethodType.TARJETA_DEBITO},
        {"name": "Tarjeta de Crédito", "type": PaymentMethodType.TARJETA_CREDITO},
    ]
    for pm in payment_methods_seed:
        exists = db.query(PaymentMethod).filter(PaymentMethod.type == pm["type"]).first()
        if not exists:
            db.add(PaymentMethod(name=pm["name"], type=pm["type"], is_active=True))
    db.commit()

    categories_seed = [
        {"name": "Alimentos y Bebidas",          "description": "Productos alimenticios, bebidas, snacks y conservas"},
        {"name": "Aseo del Hogar",                "description": "Detergentes, desinfectantes, esponjas y productos de limpieza"},
        {"name": "Aseo Personal",                 "description": "Shampoo, jabón, desodorante, cuidado bucal y cosmética"},
        {"name": "Artículos para el Hogar",       "description": "Utensilios de cocina, decoración, muebles y accesorios del hogar"},
        {"name": "Electrónica y Tecnología",      "description": "Computadores, celulares, accesorios y gadgets"},
        {"name": "Repuestos Automotrices",        "description": "Piezas y accesorios para vehículos, aceites y lubricantes"},
        {"name": "Repuestos de Electrodomésticos","description": "Piezas y accesorios para lavadoras, refrigeradores y otros electrodomésticos"},
        {"name": "Materiales de Construcción",   "description": "Cemento, pinturas, herramientas, fierros y materiales de obra"},
        {"name": "Ferretería",                    "description": "Tornillos, herramientas manuales, llaves, pernos y accesorios"},
        {"name": "Jardín y Exterior",             "description": "Plantas, tierra, fertilizantes, herramientas de jardín y outdoor"},
        {"name": "Ropa y Calzado",                "description": "Vestuario, zapatos, accesorios de moda y textiles"},
        {"name": "Juguetes y Juegos",             "description": "Juguetes infantiles, juegos de mesa y artículos recreativos"},
        {"name": "Deportes y Fitness",            "description": "Equipamiento deportivo, ropa deportiva y accesorios fitness"},
        {"name": "Librería y Papelería",          "description": "Cuadernos, lápices, artículos de oficina y escolares"},
        {"name": "Medicamentos y Salud",          "description": "Medicamentos de venta libre, vitaminas y productos de salud"},
        {"name": "Mascotas",                      "description": "Alimentos, accesorios y cuidado para animales domésticos"},
        {"name": "Otros",                         "description": "Productos varios no clasificados en otras categorías"},
    ]
    for cat in categories_seed:
        exists = db.query(Category).filter(Category.name == cat["name"]).first()
        if not exists:
            db.add(Category(name=cat["name"], description=cat["description"], is_active=True))
    db.commit()
