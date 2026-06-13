from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario, Rol, Permiso, UsuarioRol, RolPermiso
from app.auth import get_current_user, hash_password
from app.rbac import es_admin
from app.schemas.auth import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

# ========== USUARIOS ==========

@router.get("/usuarios", response_model=List[UsuarioResponse])
async def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Lista todos los usuarios (solo admin)."""
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    usuario: UsuarioCreate,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Crea un nuevo usuario (solo admin)."""
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

@router.get("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Obtiene detalle de un usuario (solo admin)."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return usuario

@router.put("/usuarios/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_update: UsuarioUpdate,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Actualiza un usuario (solo admin)."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    datos_actualizar = usuario_update.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario

@router.post("/usuarios/{usuario_id}/activar")
async def activar_usuario(
    usuario_id: int,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Activa un usuario (solo admin)."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = True
    db.commit()
    return {"message": f"Usuario {usuario_id} activado"}

@router.post("/usuarios/{usuario_id}/desactivar")
async def desactivar_usuario(
    usuario_id: int,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Desactiva un usuario (solo admin)."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.activo = False
    db.commit()
    return {"message": f"Usuario {usuario_id} desactivado"}

# ========== ROLES ==========

@router.get("/roles")
async def listar_roles(
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Lista todos los roles (solo admin)."""
    roles = db.query(Rol).all()
    return [{
        "id": r.id,
        "nombre": r.nombre,
        "descripcion": r.descripcion,
        "permisos": [p.clave for p in r.roles_permisos if p.permiso]
    } for r in roles]

@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def crear_rol(
    nombre: str,
    descripcion: str = None,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Crea un nuevo rol (solo admin)."""
    if db.query(Rol).filter(Rol.nombre == nombre).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol ya existe"
        )

    rol = Rol(nombre=nombre, descripcion=descripcion)
    db.add(rol)
    db.commit()
    db.refresh(rol)

    return {
        "id": rol.id,
        "nombre": rol.nombre,
        "descripcion": rol.descripcion
    }

# ========== USUARIO-ROLE ==========

@router.post("/usuarios/{usuario_id}/asignar-rol/{rol_id}")
async def asignar_rol_a_usuario(
    usuario_id: int,
    rol_id: int,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Asigna un rol a un usuario (solo admin)."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    # Verificar si ya tiene el rol
    if db.query(UsuarioRol).filter(
        UsuarioRol.usuario_id == usuario_id,
        UsuarioRol.rol_id == rol_id
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene este rol"
        )

    db.add(UsuarioRol(usuario_id=usuario_id, rol_id=rol_id))
    db.commit()

    return {"message": f"Rol {rol.nombre} asignado a usuario {usuario_id}"}

@router.delete("/usuarios/{usuario_id}/remover-rol/{rol_id}")
async def remover_rol_de_usuario(
    usuario_id: int,
    rol_id: int,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Remueve un rol de un usuario (solo admin)."""
    ur = db.query(UsuarioRol).filter(
        UsuarioRol.usuario_id == usuario_id,
        UsuarioRol.rol_id == rol_id
    ).first()

    if not ur:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    db.delete(ur)
    db.commit()

    return {"message": f"Rol removido del usuario {usuario_id}"}

# ========== PERMISOS ==========

@router.get("/permisos")
async def listar_permisos(
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Lista todos los permisos (solo admin)."""
    permisos = db.query(Permiso).all()
    return [{"id": p.id, "clave": p.clave} for p in permisos]

@router.post("/roles/{rol_id}/asignar-permiso/{permiso_id}")
async def asignar_permiso_a_rol(
    rol_id: int,
    permiso_id: int,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Asigna un permiso a un rol (solo admin)."""
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    permiso = db.query(Permiso).filter(Permiso.id == permiso_id).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")

    if db.query(RolPermiso).filter(
        RolPermiso.rol_id == rol_id,
        RolPermiso.permiso_id == permiso_id
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol ya tiene este permiso"
        )

    db.add(RolPermiso(rol_id=rol_id, permiso_id=permiso_id))
    db.commit()

    return {"message": f"Permiso {permiso.clave} asignado al rol {rol.nombre}"}

@router.delete("/roles/{rol_id}/remover-permiso/{permiso_id}")
async def remover_permiso_de_rol(
    rol_id: int,
    permiso_id: int,
    usuario_admin: Usuario = Depends(es_admin),
    db: Session = Depends(get_db)
):
    """Remueve un permiso de un rol (solo admin)."""
    rp = db.query(RolPermiso).filter(
        RolPermiso.rol_id == rol_id,
        RolPermiso.permiso_id == permiso_id
    ).first()

    if not rp:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    db.delete(rp)
    db.commit()

    return {"message": "Permiso removido del rol"}
