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
- ⏳ **Pendiente confirmar:** D-1 (base de cuotas: Neto vs Total con IVA) y D-2 (backend: FastAPI vs NestJS).
- ⏭️ **Siguiente:** afinar DDL definitivo → `docker-compose.yml` para el NAS → andamiar repo (Fase 0).

## Decisiones abiertas (bloqueantes)
- **D-1 — Base de cuotas:** contradicción heredada. CLAUDE.md viejo decía *Total con IVA*; README V3.0 decía *Neto*. El modelo soporta ambas (`ventas.base_cobranza`). **Confirmar con el negocio.**
- **D-2 — Backend:** FastAPI (Python, afinidad RAG/MCP) vs NestJS (TS, monorepo).
- Resto en `SDD_Mini-ERP_CNA.md` §11.

## Enrutamiento técnico
- Diseño y modelo de datos → `SDD_Mini-ERP_CNA.md`.
- Por qué se decidió cada cosa → `BITACORA.md`.
- Referencia histórica del modelo Excel → `README.md`, `Changelog.md`.
