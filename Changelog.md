# Changelog — Mini-ERP Comercial CNA

> Volver al índice: [[README]] · Decisiones asociadas: [[Decisiones_y_Pendientes]]

Formato de fechas: DD/MM/YYYY · Versión vigente: **V3.0**

---

## V3.0 — Cobranza por cuotas e interés por mora 🟢 (vigente)
- Nueva tabla **`Cuotas`** como núcleo de cobranza. Ver [[Modelo_Datos]] §6.
- **Generación automática de cuotas** al guardar la venta (N cuotas mensuales; última cuota absorbe el redondeo).
- **Interés por MORA**: 1% mensual sobre el saldo de la cuota vencida (1 día de atraso = 1 mes = 1%). Ver [[Reglas_Negocio]] §5.
- **Pagos en cascada**: abono por venta repartido de la cuota más antigua a la más nueva vía `SUMIFS`.
- `Parametros_Interes` (`TasaMensual=1%`, `DiasPorMes=30`, `IVA=19%`).
- Se abandona el interés por plazo → columnas `MesesInteres` / `AjusteManualFactor` / `FactorInteres` quedan **vestigiales**.

---

## V2.1 — Mensajería visible
- El **mensaje de aviso** (rojo/verde) queda **siempre visible** en los formularios.

## V2.0 — Venta unificada
- **Venta + Detalle unificados** en una sola hoja (`Crear_Venta_Completa`): cabecera + grilla, guardado atómico con rollback.
- Incorporación de **IVA / Total** (informativo).

---

## V1.x — Base del sistema
- Formularios de **Cliente**, **Producto**, **Venta**, **Detalle** y **Pago**.
- Hoja de **Consulta** de ventas.
- **Menú** de navegación.
- **Protección parcial** de hojas con clave `cna` y escritura por macro (`UserInterfaceOnly`).

---

## Pendiente / próximas versiones
Ver [[Decisiones_y_Pendientes]]:
- Reconexión de `Consulta_Venta`, `Crear_Pago` y `Tablero/CxC` al modelo de `Cuotas`.
- Prórroga de cuotas.
- Botón "Ver Cuotas" + `IrACuotas`.
- Pruebas finales de macros.
