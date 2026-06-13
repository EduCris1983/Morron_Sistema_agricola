from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Producto
from app.schemas import ProductoCreate, ProductoUpdate, ProductoResponse
from typing import List

router = APIRouter(prefix="/productos", tags=["productos"])

@router.get("", response_model=List[ProductoResponse])
def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    activos_solo: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Lista todos los productos con paginación."""
    query = db.query(Producto)
    if activos_solo:
        query = query.filter(Producto.activo == True)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo producto."""
    db_producto = Producto(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Obtiene un producto por ID."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return producto

@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un producto."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    datos_actualizar = producto_update.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def baja_logica_producto(producto_id: int, db: Session = Depends(get_db)):
    """Baja lógica de un producto (activo = False)."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    producto.activo = False
    db.commit()
