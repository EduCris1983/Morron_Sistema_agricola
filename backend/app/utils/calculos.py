from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from app.config import get_settings

settings = get_settings()

def calcular_neto(lineas: list) -> Decimal:
    """Calcula el neto sumando subtotales de líneas."""
    return sum(Decimal(linea.get('subtotal', 0)) for linea in lineas)

def calcular_iva(neto: Decimal) -> Decimal:
    """Calcula el IVA (19%) sobre el neto."""
    iva = neto * Decimal(settings.IVA_PCT)
    return iva.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calcular_total(neto: Decimal, iva: Decimal) -> Decimal:
    """Calcula el total (neto + iva)."""
    total = neto + iva
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calcular_margen(lineas: list) -> Decimal:
    """Calcula el margen (suma de cantidad * (precio - costo))."""
    margen = sum(
        Decimal(linea.get('cantidad', 0)) *
        (Decimal(linea.get('precio_unitario', 0)) - Decimal(linea.get('costo_unitario', 0)))
        for linea in lineas
    )
    return margen.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calcular_cuotas(base: Decimal, n_cuotas: int, fecha_base: date) -> list:
    """
    Genera cuotas mensuales basadas en la base de cobranza.
    base: monto total a financiar
    n_cuotas: número de cuotas
    fecha_base: fecha de vencimiento de la primera cuota

    Retorna lista de dicts con {numero, monto, fecha_vencimiento}
    """
    cuotas = []

    if n_cuotas <= 0:
        raise ValueError("n_cuotas debe ser >= 1")

    # Monto base de cada cuota (piso)
    monto_base = (base / Decimal(n_cuotas)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    for i in range(1, n_cuotas + 1):
        if i < n_cuotas:
            monto = monto_base
        else:
            # Última cuota absorbe el redondeo
            monto = base - (monto_base * Decimal(n_cuotas - 1))

        # Calcular fecha de vencimiento: fecha_base + (i meses)
        fecha_vencimiento = agregar_meses(fecha_base, i)

        cuotas.append({
            'numero': i,
            'monto': monto,
            'fecha_vencimiento': fecha_vencimiento,
            'estado': 'PENDIENTE'
        })

    return cuotas

def agregar_meses(fecha: date, meses: int) -> date:
    """
    Suma meses a una fecha.
    Maneja el caso de fin de mes (ej: 31/01 + 1 mes = 28/02).
    """
    mes = fecha.month + meses
    año = fecha.year

    while mes > 12:
        mes -= 12
        año += 1

    # Ajustar día si el mes destino no tiene ese día
    try:
        return fecha.replace(year=año, month=mes)
    except ValueError:
        # Caso: 31/01 + 1 mes = 28/02 (o 29 en bisiesto)
        from calendar import monthrange
        ultimo_dia = monthrange(año, mes)[1]
        return fecha.replace(year=año, month=mes, day=ultimo_dia)

def calcular_mora(saldo_cuota: Decimal, fecha_vencimiento: date, fecha_prorroga: date = None, hoy: date = None) -> Decimal:
    """
    Calcula el interés por mora.
    Parámetros:
    - saldo_cuota: monto adeudado de la cuota
    - fecha_vencimiento: fecha original de vencimiento
    - fecha_prorroga: fecha prorroga (si existe, se usa en lugar de fecha_vencimiento)
    - hoy: fecha para calcular atraso (default: today)

    Retorna el monto de interés acumulado.
    """
    if hoy is None:
        hoy = date.today()

    venc = fecha_prorroga or fecha_vencimiento
    dias_atraso = (hoy - venc).days

    if dias_atraso <= 0:
        return Decimal('0')

    # 1 día = 1 mes de mora (1%)
    meses_mora = (dias_atraso + settings.DIAS_POR_MES - 1) // settings.DIAS_POR_MES  # ceil

    interes = saldo_cuota * Decimal(settings.MORA_PCT_MENSUAL) * Decimal(meses_mora)
    return interes.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def obtener_saldo_cuota(cuota_monto: Decimal, pago_aplicaciones: list) -> Decimal:
    """Retorna el saldo capital pendiente de una cuota."""
    pagado = sum(Decimal(pa.get('monto_capital', 0)) for pa in pago_aplicaciones)
    return cuota_monto - pagado
