from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal

class CuotaResponse(BaseModel):
    id: int
    venta_id: int
    numero: int
    monto: Decimal
    fecha_vencimiento: date
    fecha_prorroga: Optional[date] = None
    estado: str

    class Config:
        from_attributes = True

class PagoAplicacionResponse(BaseModel):
    id: int
    pago_id: int
    cuota_id: int
    monto_capital: Decimal
    monto_interes: Decimal

    class Config:
        from_attributes = True

class PagoBase(BaseModel):
    venta_id: int
    fecha: date
    monto: Decimal
    medio: Optional[str] = None
    glosa: Optional[str] = None

class PagoCreate(PagoBase):
    pass

class PagoResponse(PagoBase):
    id: int
    creado_en: str
    pago_aplicaciones: Optional[list] = []

    class Config:
        from_attributes = True

class ProrrogateCuotaRequest(BaseModel):
    nueva_fecha_vencimiento: date
    recalcular_mora: bool = False
