from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cliente
from app.schemas import ClienteCreate, ClienteUpdate, ClienteResponse
from typing import List

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.get("", response_model=List[ClienteResponse])
def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    activos_solo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Lista todos los clientes con paginación."""
    query = db.query(Cliente)
    if activos_solo:
        query = query.filter(Cliente.activo == True)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Crea un nuevo cliente."""
    # Validar RUT único
    db_cliente = db.query(Cliente).filter(Cliente.rut == cliente.rut).first()
    if db_cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El RUT ya está registrado"
        )

    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtiene un cliente por ID."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente

@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un cliente."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    datos_actualizar = cliente_update.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(cliente, campo, valor)

    db.commit()
    db.refresh(cliente)
    return cliente

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def baja_logica_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Baja lógica de un cliente (activo = False)."""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    cliente.activo = False
    db.commit()
