# Mini-ERP Comercial CNA — Índice del Proyecto

> Sistema de gestión comercial para **venta de fertilizantes**, construido en un único archivo **Excel `.xlsm` con VBA**.
> Gestiona clientes, productos, ventas con detalle, pagos y **cobranza por cuotas con interés por mora**.

---

## 📌 Ficha del proyecto

| Campo | Valor |
|---|---|
| **Nombre** | Mini-ERP Comercial CNA |
| **Rubro** | Venta de fertilizantes (agrícola) |
| **Plataforma** | Excel `.xlsm` + VBA (módulos `.bas` de importación manual) |
| **Versión vigente** | **V3.0** |
| **Contraseña de hojas** | `cna` |
| **Moneda** | CLP — formato `$1.000.000,00` |
| **Fechas** | DD/MM/YYYY |
| **Estado** | En desarrollo — macros aún no testeadas en el entorno de origen |

> ⚠️ **Importación manual de VBA**: el entorno de origen no permite incrustar macros, por lo que el código se mantiene en módulos `.bas` que se importan a mano. Ver [[Macros_VBA]].

---

## 🗂️ Documentación del proyecto

- [[Modelo_Datos]] — Tablas de Excel, claves primarias, columnas de entrada vs. calculadas.
- [[Reglas_Negocio]] — Lógica de IDs, protección de hojas, validaciones, **cobranza por cuotas e interés por mora**.
- [[Macros_VBA]] — Módulos `.bas`, procedimientos públicos, helpers y patrones comunes.
- [[Decisiones_y_Pendientes]] — Decisiones cerradas y tareas abiertas.
- [[Changelog]] — Historial de versiones (V1.x → V3.0).

---

## 🧭 Mapa rápido del archivo Excel

### Hojas de datos (tablas)
`Clientes` · `Productos` · `Ventas` · `DetalleVenta` · `Pagos` · **`Cuotas`** (núcleo de cobranza V3.0) · `CxC` (modelo antiguo) · `Parametros`

### Hojas de formulario (entrada)
`Crear_Cliente` · `Crear_Producto` · `Crear_Venta_Completa` · `Crear_Pago` · `Consulta_Venta`

### Hojas de apoyo / navegación
`Menú` · `Léeme` · `Tablero` · `FichaCliente` · `SolicitudDespacho` · `Checklist_Pruebas` · `Listas` (oculta, helpers de desplegables)

---

## 🔑 Conceptos clave (V3.0)

1. **Interés solo por MORA**: 1% mensual sobre el saldo de la cuota vencida. 1 día de atraso = 1 mes = 1%. Detalle en [[Reglas_Negocio]].
2. **Cobranza sobre Neto** (el IVA 19% es informativo).
3. **Cuotas mensuales automáticas**: al guardar la venta se generan N cuotas. Ver [[Modelo_Datos]] → tabla `Cuotas`.
4. **Pagos en cascada**: los abonos se reparten de la cuota más antigua a la más nueva vía fórmulas `SUMIFS`.
5. **Macros escriben solo columnas de entrada**; las calculadas quedan por fórmula ("agujero de fórmula"). Ver [[Reglas_Negocio]].

---

## ⏭️ Próximos pasos

Ver [[Decisiones_y_Pendientes]]. En resumen:
- Reconectar `Consulta_Venta`, `Crear_Pago` y `Tablero/CxC` al modelo de `Cuotas`.
- Definir **prórroga de cuotas**.
- Agregar botón **"Ver Cuotas"** + `IrACuotas`.
- Pruebas finales de macros.
