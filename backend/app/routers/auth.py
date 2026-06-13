from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models import Usuario
from app.schemas.auth import (
    LoginRequest, TokenResponse, RefreshTokenRequest,
    UsuarioCreate, UsuarioResponse
)
from app.auth import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint de login.
    Recibe email y contraseña, retorna tokens de acceso y refresh.
    """
    # Buscar usuario por email
    usuario = db.query(Usuario).filter(Usuario.email == request.email).first()

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña inválidos"
        )

    # Verificar contraseña
    if not verify_password(request.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña inválidos"
        )

    # Crear tokens
    access_token = create_access_token(
        data={"sub": str(usuario.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": str(usuario.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Endpoint para renovar el access token usando un refresh token.
    """
    payload = verify_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )

    user_id = payload.get("sub")
    usuario = db.query(Usuario).filter(Usuario.id == int(user_id)).first()

    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no existe o está inactivo"
        )

    # Crear nuevo access token
    new_access_token = create_access_token(
        data={"sub": str(usuario.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,  # El refresh token se mantiene
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Endpoint de registro de nuevo usuario.
    Solo disponible en desarrollo. En producción, solo admin crea usuarios.
    """
    # Verificar que el email no exista
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Crear usuario
    db_usuario = Usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        password_hash=hash_password(usuario.password),
        activo=True
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return db_usuario

@router.get("/me", response_model=UsuarioResponse)
def obtener_usuario_actual(usuario: Usuario = Depends(lambda: None)):
    """
    Endpoint que retorna los datos del usuario actual.
    Requiere autenticación.

    Nota: Pendiente agregar autenticación real.
    """
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado"
        )
    return usuario
