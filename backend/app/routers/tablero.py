from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from decimal import Decimal
from datetime import date, timedelta
from app.database import get_db
from app.models import Venta, Cuota, Cliente, Pago
from app.utils.calculos import calcular_mora, obtener_saldo_cuota

router = APIRouter(prefix="/tablero", tags=["tablero"])

@router.get("")
def obtener_kpis(
    periodo_dias: int = Query(30, ge=1),
    db: Session = Depends(get_db)
):
    """
    Retorna KPIs del tablero:
    - Margen acumulado (período)
    - CxC vigente (total adeudado)
    - Cuotas vencidas
    - Top 5 deudores
    - Ingresos (pagos realizados en período)
    """
    hoy = date.today()
    fecha_inicio = hoy - timedelta(days=periodo_dias)

    # 1. Margen acumulado en el período
    ventas_periodo = db.query(Venta).filter(
        and_(
            Venta.creado_en >= fecha_inicio,
            Venta.estado != 'ANULADA'
        )
    ).all()

    margen_acumulado = Decimal('0')
    for venta in ventas_periodo:
        for linea in venta.venta_lineas:
            margen = (linea.cantidad * (linea.precio_unitario - linea.costo_unitario))
            margen_acumulado += margen

    # 2. CxC vigente (saldo total adeudado)
    ventas_vigentes = db.query(Venta).filter(Venta.estado == 'VIGENTE').all()

    cxc_vigente = Decimal('0')
    for venta in ventas_vigentes:
        cuotas = db.query(Cuota).filter(
            and_(
                Cuota.venta_id == venta.id,
                Cuota.estado.in_(['PENDIENTE', 'PARCIAL'])
            )
        ).all()

        for cuota in cuotas:
            pago_aplicaciones = [
                {'monto_capital': pa.monto_capital}
                for pa in cuota.pago_aplicaciones
            ]
            saldo = obtener_saldo_cuota(cuota.monto, pago_aplicaciones)
            cxc_vigente += saldo

    # 3. Cuotas vencidas
    cuotas_vencidas = db.query(Cuota).filter(
        and_(
            Cuota.estado.in_(['PENDIENTE', 'PARCIAL']),
            Cuota.fecha_vencimiento < hoy
        )
    ).count()

    total_mora_vencida = Decimal('0')
    cuotas_vencidas_list = db.query(Cuota).filter(
        and_(
            Cuota.estado.in_(['PENDIENTE', 'PARCIAL']),
            Cuota.fecha_vencimiento < hoy
        )
    ).all()

    for cuota in cuotas_vencidas_list:
        pago_aplicaciones = [
            {'monto_capital': pa.monto_capital}
            for pa in cuota.pago_aplicaciones
        ]
        saldo = obtener_saldo_cuota(cuota.monto, pago_aplicaciones)
        mora = calcular_mora(saldo, cuota.fecha_vencimiento, cuota.fecha_prorroga, hoy)
        total_mora_vencida += mora

    # 4. Top 5 deudores
    clientes = db.query(Cliente).filter(Cliente.activo == True).all()

    deudores = []
    for cliente in clientes:
        ventas = db.query(Venta).filter(
            and_(
                Venta.cliente_id == cliente.id,
                Venta.estado == 'VIGENTE'
            )
        ).all()

        total_cliente = Decimal('0')
        for venta in ventas:
            cuotas = db.query(Cuota).filter(
                and_(
                    Cuota.venta_id == venta.id,
                    Cuota.estado.in_(['PENDIENTE', 'PARCIAL'])
                )
            ).all()

            for cuota in cuotas:
                pago_aplicaciones = [
                    {'monto_capital': pa.monto_capital}
                    for pa in cuota.pago_aplicaciones
                ]
                saldo = obtener_saldo_cuota(cuota.monto, pago_aplicaciones)
                total_cliente += saldo

        if total_cliente > 0:
            deudores.append({
                'cliente_id': cliente.id,
                'razon_social': cliente.razon_social,
                'rut': cliente.rut,
                'deuda_total': total_cliente
            })

    deudores.sort(key=lambda x: x['deuda_total'], reverse=True)
    top_5_deudores = deudores[:5]

    # 5. Ingresos (pagos realizados en período)
    pagos_periodo = db.query(Pago).filter(
        and_(
            Pago.fecha >= fecha_inicio,
            Pago.fecha <= hoy
        )
    ).all()

    ingresos_periodo = sum(pago.monto for pago in pagos_periodo)

    return {
        'periodo': {
            'dias': periodo_dias,
            'desde': fecha_inicio.isoformat(),
            'hasta': hoy.isoformat()
        },
        'margen_acumulado': float(margen_acumulado),
        'cxc_vigente': float(cxc_vigente),
        'cuotas_vencidas': {
            'cantidad': cuotas_vencidas,
            'mora_total': float(total_mora_vencida)
        },
        'ingresos_periodo': float(ingresos_periodo),
        'top_5_deudores': top_5_deudores,
        'timestamp': hoy.isoformat()
    }

@router.get("/resumen-ventas")
def resumen_ventas(
    fecha_inicio: date = Query(None),
    fecha_fin: date = Query(None),
    db: Session = Depends(get_db)
):
    """
    Resumen de ventas por período.
    Si no se especifican fechas, usa últimos 30 días.
    """
    if fecha_fin is None:
        fecha_fin = date.today()
    if fecha_inicio is None:
        fecha_inicio = fecha_fin - timedelta(days=30)

    ventas = db.query(Venta).filter(
        and_(
            Venta.fecha_emision >= fecha_inicio,
            Venta.fecha_emision <= fecha_fin,
            Venta.estado != 'ANULADA'
        )
    ).all()

    cantidad_ventas = len(ventas)
    total_neto = sum(venta.neto for venta in ventas)
    total_iva = sum(venta.iva for venta in ventas)
    total_ingresos = sum(venta.total for venta in ventas)

    return {
        'periodo': {
            'desde': fecha_inicio.isoformat(),
            'hasta': fecha_fin.isoformat()
        },
        'cantidad_ventas': cantidad_ventas,
        'total_neto': float(total_neto),
        'total_iva': float(total_iva),
        'total_ingresos': float(total_ingresos),
        'promedio_venta': float(total_ingresos / cantidad_ventas) if cantidad_ventas > 0 else 0
    }
