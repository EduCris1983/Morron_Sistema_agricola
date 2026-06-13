from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import date
from app.database import get_db
from app.models import Venta, VentaLinea, Cuota, Cliente, Producto
from app.schemas import VentaCreate, VentaUpdate, VentaResponse, VentaDetailResponse
from app.utils.calculos import (
    calcular_neto, calcular_iva, calcular_total, calcular_margen,
    calcular_cuotas
)
from typing import List

router = APIRouter(prefix="/ventas", tags=["ventas"])

@router.get("", response_model=List[VentaResponse])
def listar_ventas(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: str = Query(None),
    cliente_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """Lista ventas con filtros opcionales."""
    query = db.query(Venta)

    if estado:
        query = query.filter(Venta.estado == estado)
    if cliente_id:
        query = query.filter(Venta.cliente_id == cliente_id)

    return query.order_by(Venta.creado_en.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=VentaResponse, status_code=status.HTTP_201_CREATED)
def crear_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva venta con líneas.

    Pasos:
    1. Valida cliente existe
    2. Calcula neto, IVA, total
    3. Genera cuotas automáticamente
    4. Persiste venta, líneas y cuotas en transacción
    """
    # Validar cliente
    cliente = db.query(Cliente).filter(Cliente.id == venta.cliente_id).first()
    if not cliente or not cliente.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cliente no existe o está inactivo"
        )

    # Validar productos en líneas
    producto_ids = [linea.producto_id for linea in venta.venta_lineas]
    productos = db.query(Producto).filter(Producto.id.in_(producto_ids)).all()
    if len(productos) != len(set(producto_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uno o más productos no existen"
        )

    # Preparar líneas con datos
    lineas_data = []
    for linea in venta.venta_lineas:
        producto = next(p for p in productos if p.id == linea.producto_id)
        lineas_data.append({
            'producto_id': linea.producto_id,
            'cantidad': linea.cantidad,
            'precio_unitario': linea.precio_unitario,
            'costo_unitario': linea.costo_unitario or producto.costo_unitario,
            'subtotal': linea.cantidad * linea.precio_unitario
        })

    # Calcular montos
    neto = calcular_neto(lineas_data)
    iva = calcular_iva(neto)
    total = calcular_total(neto, iva)

    # Crear venta
    db_venta = Venta(
        cliente_id=venta.cliente_id,
        fecha_emision=venta.fecha_emision,
        plazo_dias=venta.plazo_dias,
        n_cuotas=venta.n_cuotas,
        base_cobranza=venta.base_cobranza,
        neto=neto,
        iva=iva,
        total=total,
        estado="VIGENTE"
    )

    db.add(db_venta)
    db.flush()  # Obtener ID sin commit

    # Crear líneas
    for linea_data in lineas_data:
        db_linea = VentaLinea(
            venta_id=db_venta.id,
            producto_id=linea_data['producto_id'],
            cantidad=linea_data['cantidad'],
            precio_unitario=linea_data['precio_unitario'],
            costo_unitario=linea_data['costo_unitario'],
            subtotal=linea_data['subtotal']
        )
        db.add(db_linea)

    # Generar cuotas
    # Fecha base = fecha_emision + plazo_dias
    fecha_base = venta.fecha_emision
    if venta.plazo_dias > 0:
        from datetime import timedelta
        fecha_base = fecha_base + timedelta(days=venta.plazo_dias)

    # Base de cobranza: determinar si es NETO o TOTAL
    base_monto = neto if venta.base_cobranza == 'NETO' else total

    cuotas_data = calcular_cuotas(base_monto, venta.n_cuotas, fecha_base)

    for cuota_data in cuotas_data:
        db_cuota = Cuota(
            venta_id=db_venta.id,
            numero=cuota_data['numero'],
            monto=cuota_data['monto'],
            fecha_vencimiento=cuota_data['fecha_vencimiento'],
            estado='PENDIENTE'
        )
        db.add(db_cuota)

    db.commit()
    db.refresh(db_venta)
    return db_venta

@router.get("/{venta_id}", response_model=VentaDetailResponse)
def obtener_venta(venta_id: int, db: Session = Depends(get_db)):
    """Obtiene detalle completo de una venta con líneas, cuotas y pagos."""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )
    return venta

@router.put("/{venta_id}", response_model=VentaResponse)
def actualizar_venta(
    venta_id: int,
    venta_update: VentaUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza datos básicos de una venta (solo si está VIGENTE)."""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )

    if venta.estado != 'VIGENTE':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede editar una venta {venta.estado}"
        )

    datos_actualizar = venta_update.model_dump(exclude_unset=True)
    for campo, valor in datos_actualizar.items():
        setattr(venta, campo, valor)

    db.commit()
    db.refresh(venta)
    return venta

@router.post("/{venta_id}/anular", status_code=status.HTTP_200_OK)
def anular_venta(venta_id: int, db: Session = Depends(get_db)):
    """
    Anula una venta.

    Cambios:
    - Venta.estado = ANULADA
    - Cuotas.estado = ANULADA
    - Reversa de pagos/aplicaciones
    """
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )

    if venta.estado == 'ANULADA':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La venta ya está anulada"
        )

    # Anular venta y cuotas
    venta.estado = 'ANULADA'
    db.query(Cuota).filter(Cuota.venta_id == venta_id).update(
        {Cuota.estado: 'ANULADA'}
    )

    # Nota: Reversión de pagos sería más compleja (crear notas de crédito, etc.)
    # Por ahora solo marcamos como anulada

    db.commit()
    db.refresh(venta)

    return {"message": f"Venta {venta_id} anulada", "venta": venta}
