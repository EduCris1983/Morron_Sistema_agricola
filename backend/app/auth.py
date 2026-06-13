from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthenticationCredentials
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import Usuario
from app.database import get_db

settings = get_settings()

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Tiempos de expiración
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    """Hashea una contraseña."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Crea un JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verifica y decodifica un JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthenticationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia para obtener el usuario actual desde el token JWT.
    Se usa en los endpoints que requieren autenticación.
    """
    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    usuario = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no existe o está inactivo"
        )

    return usuario

async def get_current_user_optional(
    credentials: Optional[HTTPAuthenticationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    """
    Dependencia opcional de autenticación.
    Retorna el usuario si tiene token, None si no.
    """
    if not credentials:
        return None

    return await get_current_user(credentials, db)
