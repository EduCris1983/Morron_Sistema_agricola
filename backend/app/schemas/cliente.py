from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    razon_social: str
    rut: str
    giro: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = None
    rut: Optional[str] = None
    giro: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

class ClienteResponse(ClienteBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True
