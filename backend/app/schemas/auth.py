from pydantic import BaseModel, EmailStr
from app.models.user import RoleName


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    role_name: RoleName = RoleName.VENDEDOR


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
    role_name: RoleName | None = None


TokenResponse.model_rebuild()
