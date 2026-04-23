from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, UserCreate, UserUpdate
from app.services.auth_service import authenticate_user, create_access_token, hash_password, get_or_create_role
from app.models.user import User
from app.utils.deps import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, data.username, data.password)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            role=user.role.name.value,
        )
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        role=current_user.role.name.value,
    )


@router.get("/users", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserResponse(id=u.id, email=u.email, username=u.username,
                         full_name=u.full_name, is_active=u.is_active,
                         role=u.role.name.value) for u in users]


@router.post("/users", response_model=UserResponse, dependencies=[Depends(require_admin)])
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    role = get_or_create_role(db, data.role_name)
    user = User(
        email=data.email,
        username=data.username,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, email=user.email, username=user.username,
                        full_name=user.full_name, is_active=user.is_active,
                        role=user.role.name.value)


@router.put("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if data.email:
        user.email = data.email
    if data.full_name:
        user.full_name = data.full_name
    if data.password:
        user.hashed_password = hash_password(data.password)
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.role_name:
        role = get_or_create_role(db, data.role_name)
        user.role_id = role.id
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, email=user.email, username=user.username,
                        full_name=user.full_name, is_active=user.is_active,
                        role=user.role.name.value)
