from sqlalchemy import (
    BigInteger, String, Text, Boolean, Numeric, Date, DateTime,
    ForeignKey, CheckConstraint, UniqueConstraint, Index, func, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from datetime import datetime, date
from app.database import Base

# ========== MAESTROS ==========

class Cliente(Base):
    __tablename__ = "clientes"

    id = Base.metadata.columns["clientes.id"].__class__(BigInteger, primary_key=True)
    id = func.cast(func.nextval('clientes_id_seq'), BigInteger)  # GENERATED ALWAYS AS IDENTITY
    razon_social = Base.metadata.columns.get("razon_social", String) or String(255)
    rut = Base.metadata.columns.get("rut", String) or String(20)
    giro = String(255)
    email = String(255)
    telefono = String(20)
    direccion = Text()
    activo = Boolean(default=True)
    creado_por = BigInteger()
    creado_en = DateTime(timezone=True, server_default=func.now())
    actualizado_en = DateTime(timezone=True, server_default=func.now())

    ventas = relationship("Venta", back_populates="cliente")

    __table_args__ = (
        UniqueConstraint("rut", name="clientes_rut_unique"),
    )


class Producto(Base):
    __tablename__ = "productos"

    id = BigInteger(primary_key=True)
    nombre = String(255)
    formulacion = String(255)
    unidad = String(10, default="KG")
    costo_unitario = Numeric(14, 2, default=0)
    precio_unitario = Numeric(14, 2, default=0)
    activo = Boolean(default=True)
    creado_en = DateTime(timezone=True, server_default=func.now())
    actualizado_en = DateTime(timezone=True, server_default=func.now())

    venta_lineas = relationship("VentaLinea", back_populates="producto")


# ========== USUARIOS (RBAC) ==========

class Usuario(Base):
    __tablename__ = "usuarios"

    id = BigInteger(primary_key=True)
    email = String(255)
    nombre = String(255)
    password_hash = String(255)
    activo = Boolean(default=True)
    ultimo_acceso = DateTime(timezone=True)
    creado_en = DateTime(timezone=True, server_default=func.now())

    usuarios_roles = relationship("UsuarioRol", back_populates="usuario")

    __table_args__ = (
        UniqueConstraint("email", name="usuarios_email_unique"),
    )


class Rol(Base):
    __tablename__ = "roles"

    id = BigInteger(primary_key=True)
    nombre = String(255)
    descripcion = Text()

    usuarios_roles = relationship("UsuarioRol", back_populates="rol")
    roles_permisos = relationship("RolPermiso", back_populates="rol")

    __table_args__ = (
        UniqueConstraint("nombre", name="roles_nombre_unique"),
    )


class Permiso(Base):
    __tablename__ = "permisos"

    id = BigInteger(primary_key=True)
    clave = String(255)

    roles_permisos = relationship("RolPermiso", back_populates="permiso")

    __table_args__ = (
        UniqueConstraint("clave", name="permisos_clave_unique"),
    )


class UsuarioRol(Base):
    __tablename__ = "usuarios_roles"

    usuario_id = BigInteger(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    rol_id = BigInteger(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

    usuario = relationship("Usuario", back_populates="usuarios_roles")
    rol = relationship("Rol", back_populates="usuarios_roles")


class RolPermiso(Base):
    __tablename__ = "roles_permisos"

    rol_id = BigInteger(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permiso_id = BigInteger(ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True)

    rol = relationship("Rol", back_populates="roles_permisos")
    permiso = relationship("Permiso", back_populates="roles_permisos")


# ========== VENTAS ==========

class Venta(Base):
    __tablename__ = "ventas"

    id = BigInteger(primary_key=True)
    folio = String(255)
    cliente_id = BigInteger(ForeignKey("clientes.id"))
    fecha_emision = Date(server_default=func.current_date())
    plazo_dias = BigInteger(default=0)
    n_cuotas = BigInteger(default=1)
    base_cobranza = String(10, default="TOTAL")  # NETO | TOTAL
    neto = Numeric(14, 2, default=0)
    iva = Numeric(14, 2, default=0)
    total = Numeric(14, 2, default=0)
    estado = String(20, default="VIGENTE")  # VIGENTE | PAGADA | ANULADA
    creado_por = BigInteger(ForeignKey("usuarios.id"))
    creado_en = DateTime(timezone=True, server_default=func.now())
    actualizado_en = DateTime(timezone=True, server_default=func.now())

    cliente = relationship("Cliente", back_populates="ventas")
    venta_lineas = relationship("VentaLinea", back_populates="venta", cascade="all, delete-orphan")
    cuotas = relationship("Cuota", back_populates="venta", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="venta")

    __table_args__ = (
        UniqueConstraint("folio", name="ventas_folio_unique"),
        CheckConstraint("n_cuotas >= 1"),
        CheckConstraint("base_cobranza IN ('NETO', 'TOTAL')"),
        CheckConstraint("estado IN ('VIGENTE', 'PAGADA', 'ANULADA')"),
    )


class VentaLinea(Base):
    __tablename__ = "venta_lineas"

    id = BigInteger(primary_key=True)
    venta_id = BigInteger(ForeignKey("ventas.id", ondelete="CASCADE"))
    producto_id = BigInteger(ForeignKey("productos.id"))
    cantidad = Numeric(14, 3)
    precio_unitario = Numeric(14, 2)
    costo_unitario = Numeric(14, 2, default=0)
    subtotal = Numeric(14, 2)  # GENERATED ALWAYS AS (cantidad * precio_unitario)

    venta = relationship("Venta", back_populates="venta_lineas")
    producto = relationship("Producto", back_populates="venta_lineas")

    __table_args__ = (
        CheckConstraint("cantidad > 0"),
    )


# ========== COBRANZA POR CUOTAS ==========

class Cuota(Base):
    __tablename__ = "cuotas"

    id = BigInteger(primary_key=True)
    venta_id = BigInteger(ForeignKey("ventas.id", ondelete="CASCADE"))
    numero = BigInteger()
    monto = Numeric(14, 2)
    fecha_vencimiento = Date()
    fecha_prorroga = Date()
    estado = String(20, default="PENDIENTE")  # PENDIENTE | PARCIAL | PAGADA | ANULADA

    venta = relationship("Venta", back_populates="cuotas")
    pago_aplicaciones = relationship("PagoAplicacion", back_populates="cuota")

    __table_args__ = (
        UniqueConstraint("venta_id", "numero", name="cuotas_venta_numero_unique"),
        CheckConstraint("estado IN ('PENDIENTE', 'PARCIAL', 'PAGADA', 'ANULADA')"),
    )


# ========== PAGOS (en cascada) ==========

class Pago(Base):
    __tablename__ = "pagos"

    id = BigInteger(primary_key=True)
    venta_id = BigInteger(ForeignKey("ventas.id"))
    fecha = Date(server_default=func.current_date())
    monto = Numeric(14, 2)
    medio = String(255)  # transferencia, efectivo, encomienda...
    glosa = Text()
    creado_por = BigInteger(ForeignKey("usuarios.id"))
    creado_en = DateTime(timezone=True, server_default=func.now())

    venta = relationship("Venta", back_populates="pagos")
    pago_aplicaciones = relationship("PagoAplicacion", back_populates="pago", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("monto > 0"),
    )


class PagoAplicacion(Base):
    __tablename__ = "pago_aplicaciones"

    id = BigInteger(primary_key=True)
    pago_id = BigInteger(ForeignKey("pagos.id", ondelete="CASCADE"))
    cuota_id = BigInteger(ForeignKey("cuotas.id"))
    monto_capital = Numeric(14, 2, default=0)
    monto_interes = Numeric(14, 2, default=0)

    pago = relationship("Pago", back_populates="pago_aplicaciones")
    cuota = relationship("Cuota", back_populates="pago_aplicaciones")


# ========== PARÁMETROS ==========

class Parametro(Base):
    __tablename__ = "parametros"

    clave = String(255, primary_key=True)
    valor = String(255)
    descripcion = Text()


# ========== AUDITORÍA ==========

class Auditoria(Base):
    __tablename__ = "auditoria"

    id = BigInteger(primary_key=True)
    usuario_id = BigInteger(ForeignKey("usuarios.id"))
    entidad = String(255)
    entidad_id = BigInteger()
    accion = String(255)  # crear/editar/anular
    detalle = JSON()
    creado_en = DateTime(timezone=True, server_default=func.now())


# ========== RAG ==========

class Documento(Base):
    __tablename__ = "documentos"

    id = BigInteger(primary_key=True)
    tipo = String(255)
    titulo = String(255)
    origen = String(255)
    entidad_rel = String(255)
    entidad_rel_id = BigInteger()
    metadata = JSON()
    creado_en = DateTime(timezone=True, server_default=func.now())

    documento_chunks = relationship("DocumentoChunk", back_populates="documento", cascade="all, delete-orphan")


class DocumentoChunk(Base):
    __tablename__ = "documento_chunks"

    id = BigInteger(primary_key=True)
    documento_id = BigInteger(ForeignKey("documentos.id", ondelete="CASCADE"))
    contenido = Text()
    embedding = Vector(1536)  # pgvector
    chunk_idx = BigInteger()
    metadata = JSON()

    documento = relationship("Documento", back_populates="documento_chunks")

    __table_args__ = (
        Index("idx_chunks_embedding", "embedding", postgresql_using="hnsw"),
    )
