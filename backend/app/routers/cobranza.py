from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
from datetime import date
from app.database import get_db
from app.models import Venta, Cuota, Pago, PagoAplicacion, Cliente
from app.schemas import (
    PagoCreate, PagoResponse, CuotaResponse, ProrrogateCuotaRequest
)
from app.utils.calculos import calcular_mora, obtener_saldo_cuota, agregar_meses
from typing import List

router = APIRouter(prefix="/cobranza", tags=["cobranza"])

@router.get("/cuotas-vencidas", response_model=List[CuotaResponse])
def listar_cuotas_vencidas(
    hoy: date = Query(None),
    cliente_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """
    Lista cuotas vencidas (pendientes o parciales con atraso).

    hoy: fecha para calcular atraso (default: today)
    cliente_id: filtrar por cliente
    """
    if hoy is None:
        hoy = date.today()

    query = db.query(Cuota).filter(
        Cuota.estado.in_(['PENDIENTE', 'PARCIAL']),
        Cuota.fecha_vencimiento < hoy  # Vencidas
    )

    if cliente_id:
        query = query.join(Venta).filter(Venta.cliente_id == cliente_id)

    return query.all()

@router.post("/pagos", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def registrar_pago(pago: PagoCreate, db: Session = Depends(get_db)):
    """
    Registra un pago y lo aplica en cascada (de la cuota más antigua a la más nueva).

    Flujo:
    1. Valida venta existe
    2. Obtiene cuotas pendientes/parciales ordenadas por número
    3. Para cada cuota:
       - Calcula mora acumulada
       - Aplica pago: primero a interés, luego a capital
       - Actualiza estado de cuota
    4. Si venta queda sin saldo, marca como PAGADA
    5. Persiste pago + aplicaciones en una transacción
    """
    # Validar venta
    venta = db.query(Venta).filter(Venta.id == pago.venta_id).first()
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Venta no existe"
        )

    if venta.estado != 'VIGENTE':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede pagar una venta {venta.estado}"
        )

    # Crear pago
    db_pago = Pago(
        venta_id=pago.venta_id,
        fecha=pago.fecha,
        monto=pago.monto,
        medio=pago.medio,
        glosa=pago.glosa
    )
    db.add(db_pago)
    db.flush()  # Obtener ID

    # Obtener cuotas pendientes/parciales (más antiguas primero)
    cuotas = db.query(Cuota).filter(
        and_(
            Cuota.venta_id == pago.venta_id,
            Cuota.estado.in_(['PENDIENTE', 'PARCIAL'])
        )
    ).order_by(Cuota.numero).all()

    if not cuotas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay cuotas pendientes para esta venta"
        )

    # Aplicar pago en cascada
    monto_restante = pago.monto
    total_venta_saldo = Decimal('0')

    for cuota in cuotas:
        if monto_restante <= 0:
            break

        # Obtener saldo de la cuota (capital pendiente)
        pago_aplicaciones_previas = db.query(PagoAplicacion).filter(
            PagoAplicacion.cuota_id == cuota.id
        ).all()

        saldo_capital = obtener_saldo_cuota(cuota.monto, [
            {'monto_capital': pa.monto_capital} for pa in pago_aplicaciones_previas
        ])

        # Calcular mora
        mora = calcular_mora(
            saldo_capital,
            cuota.fecha_vencimiento,
            cuota.fecha_prorroga,
            pago.fecha
        )

        # Aplicar: primero mora, luego capital
        monto_interes = min(mora, monto_restante)
        monto_restante -= monto_interes

        monto_capital = min(saldo_capital, monto_restante)
        monto_restante -= monto_capital

        # Crear aplicación
        db_aplicacion = PagoAplicacion(
            pago_id=db_pago.id,
            cuota_id=cuota.id,
            monto_capital=monto_capital,
            monto_interes=monto_interes
        )
        db.add(db_aplicacion)

        # Actualizar estado de cuota
        nuevo_saldo = saldo_capital - monto_capital
        if nuevo_saldo <= 0:
            cuota.estado = 'PAGADA'
        else:
            cuota.estado = 'PARCIAL'

        total_venta_saldo += nuevo_saldo

    # Actualizar estado de venta
    if total_venta_saldo <= 0:
        venta.estado = 'PAGADA'

    db.commit()
    db.refresh(db_pago)
    return db_pago

@router.post("/cuotas/{cuota_id}/prorroga")
def prorrogar_cuota(
    cuota_id: int,
    request: ProrrogateCuotaRequest,
    db: Session = Depends(get_db)
):
    """
    Prorroga una cuota a una nueva fecha de vencimiento.

    Si recalcular_mora=true, se ajusta el saldo considerando la nueva mora hasta la fecha de prórroga.
    """
    cuota = db.query(Cuota).filter(Cuota.id == cuota_id).first()
    if not cuota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuota no encontrada"
        )

    if cuota.estado == 'PAGADA':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede prorrogar una cuota pagada"
        )

    # Actualizar fecha de prórroga
    cuota.fecha_prorroga = request.nueva_fecha_vencimiento

    # Si recalcular_mora, calcular mora acumulada hasta la nueva fecha
    if request.recalcular_mora:
        pago_aplicaciones = db.query(PagoAplicacion).filter(
            PagoAplicacion.cuota_id == cuota_id
        ).all()
        saldo = obtener_saldo_cuota(cuota.monto, [
            {'monto_capital': pa.monto_capital} for pa in pago_aplicaciones
        ])

        mora = calcular_mora(
            saldo,
            cuota.fecha_vencimiento,
            request.nueva_fecha_vencimiento,
            date.today()
        )

        # Nota: La mora se cobra cuando se paga, no se suma al monto de la cuota
        # Solo se registra la prórroga

    db.commit()
    db.refresh(cuota)

    return {
        "message": f"Cuota {cuota_id} prorroga a {request.nueva_fecha_vencimiento}",
        "cuota": cuota
    }

@router.get("/clientes/{cliente_id}/estado-cuenta")
def estado_cuenta_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Retorna el estado de cuenta de un cliente:
    - Cuotas pendientes/parciales
    - Total adeudado (capital + mora)
    - Cuotas vencidas
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )

    hoy = date.today()

    # Obtener ventas vigentes
    ventas = db.query(Venta).filter(
        and_(
            Venta.cliente_id == cliente_id,
            Venta.estado == 'VIGENTE'
        )
    ).all()

    cuotas_pendientes = []
    cuotas_vencidas = []
    total_adeudado = Decimal('0')
    total_mora = Decimal('0')

    for venta in ventas:
        cuotas = db.query(Cuota).filter(
            and_(
                Cuota.venta_id == venta.id,
                Cuota.estado.in_(['PENDIENTE', 'PARCIAL'])
            )
        ).all()

        for cuota in cuotas:
            pago_aplicaciones = db.query(PagoAplicacion).filter(
                PagoAplicacion.cuota_id == cuota.id
            ).all()

            saldo_capital = obtener_saldo_cuota(cuota.monto, [
                {'monto_capital': pa.monto_capital} for pa in pago_aplicaciones
            ])

            mora = calcular_mora(
                saldo_capital,
                cuota.fecha_vencimiento,
                cuota.fecha_prorroga,
                hoy
            )

            cuota_dict = {
                'cuota_id': cuota.id,
                'venta_id': venta.id,
                'numero': cuota.numero,
                'monto_capital': cuota.monto,
                'saldo_capital': saldo_capital,
                'mora_acumulada': mora,
                'fecha_vencimiento': cuota.fecha_vencimiento,
                'fecha_prorroga': cuota.fecha_prorroga,
                'estado': cuota.estado
            }

            total_adeudado += saldo_capital
            total_mora += mora

            if cuota.fecha_vencimiento < hoy and saldo_capital > 0:
                cuotas_vencidas.append(cuota_dict)
            else:
                cuotas_pendientes.append(cuota_dict)

    return {
        'cliente': {
            'id': cliente.id,
            'razon_social': cliente.razon_social,
            'rut': cliente.rut
        },
        'cuotas_pendientes': cuotas_pendientes,
        'cuotas_vencidas': cuotas_vencidas,
        'total_adeudado': total_adeudado,
        'total_mora': total_mora,
        'total_con_mora': total_adeudado + total_mora
    }
