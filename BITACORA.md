# Bitácora — Mini-ERP Comercial CNA

> Registro cronológico de avances y decisiones clave. Lo más reciente arriba.
> Documentos relacionados: `CLAUDE.md` (instrucciones), `SDD_Mini-ERP_CNA.md` (diseño).
> Fechas DD/MM/YYYY.

---

## 12/06/2026 — Redacción del SDD de la app web

**Avances**
- Se creó `SDD_Mini-ERP_CNA.md` con el diseño completo:
  - Arquitectura en NAS (Docker Compose: proxy HTTPS, frontend, API, Postgres+pgvector, MCP).
  - Modelo de datos con **DDL SQL** para dominio (clientes, productos, ventas, líneas, cuotas, pagos, aplicaciones en cascada, parámetros), **RBAC** (usuarios, roles, permisos, auditoría) y **RAG** (documentos + chunks con `vector` e índice HNSW).
  - Reglas de negocio, API REST, frontend, seguridad, roadmap por fases.
- Se actualizó `CLAUDE.md` al nuevo rumbo y se inició esta bitácora.

**Decisiones tomadas**
- **Plataforma:** app web self-hosted en NAS (no más Excel/VBA).
- **Stack:** React + TS + Vite + shadcn/ui (front); PostgreSQL 16 + pgvector (BD); Docker Compose (despliegue).
- **Backend propuesto:** FastAPI (Python) por afinidad con RAG y MCP — *a confirmar*.
- **Estructura preparada desde el día 1** para multiusuario/perfiles (RBAC), RAG y MCP con Claude.

**Decisiones pendientes (bloqueantes)**
- **D-1 — Base de cuotas:** Neto (README V3.0) vs Total con IVA (CLAUDE.md viejo). El modelo soporta ambas vía `ventas.base_cobranza`. Falta confirmación del negocio.
- **D-2 — Backend:** FastAPI (Python) vs NestJS (TypeScript, monorepo).
- D-3: orden de aplicación del pago (interés→capital vs capital→interés).
- D-4: fecha base de cuotas (emisión vs emisión + plazo).
- D-5: ¿migrar histórico 2025/2026 del Excel?

**Siguiente paso**
- Confirmar D-1 y D-2 → afinar DDL definitivo → generar `docker-compose.yml` → andamiar repo (Fase 0).

---

## 12/06/2026 — Revisión inicial de la carpeta

**Hallazgos**
- La documentación (CLAUDE.md/README/Changelog) describía un **Mini-ERP Excel `.xlsm` + VBA** que **no existe** en la carpeta.
- El archivo real `FERTILIZANTES CNA 2025.xlsx` es la **planilla manual heredada** (origen: Alex Niklitschek), con 4 hojas planas: `FERT CNA 2025`, `RESUMEN PAGOS 2025`, `FERT CNA 2026`, `Hoja1`.
- Faltan los documentos enlazados (`Estado_Proyecto.md`, `Modelo_Datos.md`, `Reglas_Negocio.md`, etc.).
- Inconsistencias en datos heredados a validar antes de migrar:
  - RUT distinto para "GABRIEL SEGUND" (`8163012-7` vs `8163012-8`).
  - Fecha como texto `11-04.2027` en FERT CNA 2026.
  - Folio 67633: vencimiento anterior a la emisión.
  - `Hoja1` parece borrador/scratch.
- La planilla real calcula interés **por plazo** (columna `FACTOR`), modelo que el README decía haber **abandonado** en favor de mora.

**Decisión**
- Tras esta revisión, el usuario pidió pivotar a una **app web** (ver entrada del 12/06/2026 arriba).
