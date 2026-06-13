from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class VentaLineaBase(BaseModel):
    producto_id: int
    cantidad: Decimal
    precio_unitario: Decimal
    costo_unitario: Optional[Decimal] = 0

class VentaLineaCreate(VentaLineaBase):
    pass

class VentaLineaResponse(VentaLineaBase):
    id: int
    venta_id: int
    subtotal: Decimal

    class Config:
        from_attributes = True

class VentaBase(BaseModel):
    cliente_id: int
    fecha_emision: date
    plazo_dias: int = 0
    n_cuotas: int = 1
    base_cobranza: str = "TOTAL"  # NETO | TOTAL

class VentaCreate(VentaBase):
    venta_lineas: List[VentaLineaCreate]

class VentaUpdate(BaseModel):
    fecha_emision: Optional[date] = None
    plazo_dias: Optional[int] = None
    n_cuotas: Optional[int] = None
    base_cobranza: Optional[str] = None

class VentaResponse(VentaBase):
    id: int
    folio: Optional[str]
    neto: Decimal
    iva: Decimal
    total: Decimal
    estado: str
    creado_en: datetime
    actualizado_en: datetime
    venta_lineas: List[VentaLineaResponse] = []

    class Config:
        from_attributes = True

class VentaDetailResponse(VentaResponse):
    cuotas: Optional[List] = []
    pagos: Optional[List] = []
