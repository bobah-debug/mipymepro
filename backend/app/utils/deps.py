from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import decode_token
from app.models.user import User, RoleName


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user


def require_role(*roles: RoleName):
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol requerido: {', '.join(r.value for r in roles)}"
            )
        return current_user
    return checker


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name != RoleName.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    return current_user
