from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ProductoBase(BaseModel):
    nombre: str
    formulacion: Optional[str] = None
    unidad: str = "KG"
    costo_unitario: Decimal
    precio_unitario: Decimal
    activo: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    formulacion: Optional[str] = None
    unidad: Optional[str] = None
    costo_unitario: Optional[Decimal] = None
    precio_unitario: Optional[Decimal] = None
    activo: Optional[bool] = None

class ProductoResponse(ProductoBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True
