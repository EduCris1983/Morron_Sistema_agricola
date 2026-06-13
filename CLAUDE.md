# Mini-ERP Comercial CNA — Instrucciones del proyecto

> Diseño completo en `SDD_Mini-ERP_CNA.md`. Historial de decisiones en `BITACORA.md`.
> No dupliques ese contenido aquí: léelo.

## Qué es (rumbo vigente)
**Aplicación web self-hosted** para la **venta de fertilizantes** (rubro agrícola, cliente CNA — Alex Niklitschek). Reemplaza la planilla manual `FERTILIZANTES CNA 2025.xlsx`.

Cubre cuatro dominios:
- **Maestros:** alta de clientes y productos.
- **Ventas:** registro con detalle de líneas; cálculo de Neto + IVA 19% + Total.
- **Cobranza por cuotas:** cuotas mensuales con **interés por mora** (1% mensual sobre el saldo de la cuota vencida; 1 día = 1 mes = 1%).
- **Pagos en cascada:** los abonos se reparten de la cuota más antigua a la más nueva.

> ⚠️ **Cambio de plataforma (12/06/2026):** el proyecto migró de Excel `.xlsm` + VBA a app web. La documentación antigua (`README.md`, `Changelog.md`) describe el modelo Excel y queda como **referencia histórica**. El Excel `.xlsx` es ahora solo **fuente de datos a migrar**.

## Stack
- **Frontend:** React + TypeScript + Vite + shadcn/ui + Tailwind.
- **Backend:** FastAPI (Python) — *propuesto, por confirmar (ver D-2)*.
- **BD:** PostgreSQL 16 + `pgvector` (RAG futuro).
- **Despliegue:** Docker Compose en NAS, detrás de reverse proxy con HTTPS.
- **Control de usuarios:** RBAC (usuarios, roles, permisos, auditoría) desde el MVP.
- **Futuro:** RAG (tablas `documentos`/`documento_chunks`) y un **MCP** conectable a Claude.

## Convenciones del proyecto
- Moneda CLP `$1.000.000,00` · fechas DD/MM/YYYY · español latinoamericano.
- Separador de miles `.` y decimal `,`.
- Montos en BD como `numeric(14,2)`; baja lógica con `activo`/`estado`, no DELETE físico.
- Migraciones de BD versionadas (Alembic); nada de cambios manuales al esquema.

## Estado actual (avances)
- ✅ Revisión de la carpeta y del Excel heredado.
- ✅ **SDD redactado** (`SDD_Mini-ERP_CNA.md`): arquitectura, DDL completo (dominio + RBAC + RAG), reglas de negocio, API, roadmap.
- ✅ Bitácora iniciada (`BITACORA.md`).
- ✅ **Fase 0 completada:** Andamiaje (docker-compose, .env, DDL, estructura).
- ✅ **Fase 1 completada:** Backend (1000+ líneas), Frontend (1000+ líneas), Autenticación JWT.
- ✅ **Fase 2 completada:** Alembic (migraciones versionadas), RBAC (17 permisos granulares), Frontend completo (5 páginas).
- ⏳ **Listo para testing:** puerto frontend 5175, API 8000, PostgreSQL 5432 (requiere Docker + reinicio PC).
- ⏭️ **Siguiente:** Levantar con Docker Desktop → testear flujos completos → RAG + MCP (futuro).

## Decisiones confirmadas ✅
- **D-1 — Base de cuotas:** ✅ **Total con IVA** (implementado en Venta.base_cobranza)
- **D-2 — Backend:** ✅ **FastAPI (Python)** (completamente implementado)
- **D-3 — Orden pago mora:** ✅ **Interés→Capital** (implementado en cobranza)
- **D-4 — Fecha base cuotas:** ✅ **Emisión + plazo** (implementado en calcular_cuotas)
- Resto en `SDD_Mini-ERP_CNA.md` §11.

## Enrutamiento técnico
- Diseño y modelo de datos → `SDD_Mini-ERP_CNA.md`.
- Por qué se decidió cada cosa → `BITACORA.md`.
- Referencia histórica del modelo Excel → `README.md`, `Changelog.md`.
