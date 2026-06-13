from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    activo: bool

    class Config:
        from_attributes = True

class UsuarioCreate(BaseModel):
    email: EmailStr
    nombre: str
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
