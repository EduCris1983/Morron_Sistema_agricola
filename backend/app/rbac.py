from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import Usuario, Rol, RolPermiso, Permiso
from app.auth import get_current_user
from app.database import get_db
from typing import List

async def verificar_permiso(
    permiso_requerido: str,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que verifica si el usuario actual tiene un permiso específico.

    Uso en endpoint:
        @router.post("/algo")
        def crear_algo(
            usuario: Usuario = Depends(lambda: verificar_permiso("ventas.crear")),
            db: Session = Depends(get_db)
        ):
            ...
    """
    # Obtener roles del usuario
    roles = db.query(Rol).join(Usuario.usuarios_roles).filter(
        Usuario.id == usuario.id
    ).all()

    # Buscar permisos en los roles del usuario
    permisos = db.query(Permiso).join(RolPermiso).join(Rol).filter(
        Rol.id.in_([r.id for r in roles])
    ).all()

    permisos_clave = [p.clave for p in permisos]

    if permiso_requerido not in permisos_clave:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No tiene permiso para: {permiso_requerido}"
        )

    return usuario

async def es_admin(
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que verifica si el usuario es admin.
    """
    rol_admin = db.query(Rol).filter(Rol.nombre == 'admin').first()

    if not rol_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no autenticado o no es admin"
        )

    # Verificar si el usuario tiene el rol admin
    tiene_admin = db.query(Usuario).join(Usuario.usuarios_roles).filter(
        Usuario.id == usuario.id,
        Rol.id == rol_admin.id
    ).first()

    if not tiene_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No es admin"
        )

    return usuario

def crear_permisos_iniciales(db: Session) -> None:
    """
    Crea los permisos iniciales en la BD.
    Se ejecuta una sola vez al iniciar.
    """
    permisos_data = [
        # Clientes
        ('clientes.crear', 'Crear clientes'),
        ('clientes.editar', 'Editar clientes'),
        ('clientes.leer', 'Leer clientes'),
        ('clientes.eliminar', 'Eliminar (baja lógica) clientes'),

        # Productos
        ('productos.crear', 'Crear productos'),
        ('productos.editar', 'Editar productos'),
        ('productos.leer', 'Leer productos'),
        ('productos.eliminar', 'Eliminar (baja lógica) productos'),

        # Ventas
        ('ventas.crear', 'Crear ventas'),
        ('ventas.editar', 'Editar ventas'),
        ('ventas.leer', 'Leer ventas'),
        ('ventas.anular', 'Anular ventas'),

        # Cobranza
        ('cobranza.crear_pago', 'Registrar pagos'),
        ('cobranza.prorrogar', 'Prorrogar cuotas'),
        ('cobranza.leer', 'Leer estado de cobranza'),

        # Tablero
        ('tablero.leer', 'Ver tablero y KPIs'),

        # Admin
        ('admin', 'Acceso administrativo total'),
    ]

    for clave, descripcion in permisos_data:
        if not db.query(Permiso).filter(Permiso.clave == clave).first():
            db.add(Permiso(clave=clave))

    db.commit()

def asignar_permisos_a_roles(db: Session) -> None:
    """
    Asigna permisos iniciales a los roles.
    Se ejecuta una sola vez al iniciar.
    """
    # Admin: todos los permisos
    rol_admin = db.query(Rol).filter(Rol.nombre == 'admin').first()
    if rol_admin:
        permisos = db.query(Permiso).all()
        for permiso in permisos:
            if not db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_admin.id,
                RolPermiso.permiso_id == permiso.id
            ).first():
                db.add(RolPermiso(rol_id=rol_admin.id, permiso_id=permiso.id))

    # Vendedor: crear/leer ventas y clientes, leer tablero
    rol_vendedor = db.query(Rol).filter(Rol.nombre == 'vendedor').first()
    if rol_vendedor:
        permisos_vendedor = [
            'clientes.crear', 'clientes.editar', 'clientes.leer',
            'productos.leer',
            'ventas.crear', 'ventas.leer',
            'tablero.leer'
        ]
        for clave in permisos_vendedor:
            permiso = db.query(Permiso).filter(Permiso.clave == clave).first()
            if permiso and not db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_vendedor.id,
                RolPermiso.permiso_id == permiso.id
            ).first():
                db.add(RolPermiso(rol_id=rol_vendedor.id, permiso_id=permiso.id))

    # Cobranza: crear pagos, prorrogar, leer ventas/cobranza, ver tablero
    rol_cobranza = db.query(Rol).filter(Rol.nombre == 'cobranza').first()
    if rol_cobranza:
        permisos_cobranza = [
            'clientes.leer',
            'ventas.leer',
            'cobranza.crear_pago', 'cobranza.prorrogar', 'cobranza.leer',
            'tablero.leer'
        ]
        for clave in permisos_cobranza:
            permiso = db.query(Permiso).filter(Permiso.clave == clave).first()
            if permiso and not db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_cobranza.id,
                RolPermiso.permiso_id == permiso.id
            ).first():
                db.add(RolPermiso(rol_id=rol_cobranza.id, permiso_id=permiso.id))

    # Lectura: solo leer todo
    rol_lectura = db.query(Rol).filter(Rol.nombre == 'lectura').first()
    if rol_lectura:
        permisos_lectura = [
            'clientes.leer',
            'productos.leer',
            'ventas.leer',
            'cobranza.leer',
            'tablero.leer'
        ]
        for clave in permisos_lectura:
            permiso = db.query(Permiso).filter(Permiso.clave == clave).first()
            if permiso and not db.query(RolPermiso).filter(
                RolPermiso.rol_id == rol_lectura.id,
                RolPermiso.permiso_id == permiso.id
            ).first():
                db.add(RolPermiso(rol_id=rol_lectura.id, permiso_id=permiso.id))

    db.commit()
