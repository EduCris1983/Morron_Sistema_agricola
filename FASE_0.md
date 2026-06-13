# Fase 0 — Andamiaje del Proyecto

**Estado:** ✅ Completado - Estructura base creada

**Decisiones confirmadas:**
- D-1: Base de cuotas → **Total con IVA**
- D-2: Backend → **FastAPI (Python)**

## Estructura del proyecto

```
.
├── frontend/                    # React + TypeScript + Vite + Tailwind
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile.dev
│
├── backend/                     # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker/
│   └── postgres/
│       └── init.sql             # DDL completo (maestros, dominio, RBAC, RAG)
│
├── migrations/                  # Alembic migrations (futuro)
│
├── docker-compose.yml           # Orquestación: Postgres, API, Frontend
├── .env.example                 # Variables de entorno
├── .gitignore
└── FASE_0.md                    # Este archivo
```

## Componentes iniciados

### 1. Backend (FastAPI)
- ✅ Estructura de directorios
- ✅ `main.py`: aplicación FastAPI con CORS
- ✅ `config.py`: configuración con pydantic-settings
- ✅ `database.py`: conexión SQLAlchemy + SessionLocal
- ✅ `requirements.txt`: dependencias Python
- ✅ `Dockerfile`: imagen para FastAPI
- ⏳ Modelos SQLAlchemy (próximo)
- ⏳ Rutas API (próximo)

### 2. Frontend (React + Vite)
- ✅ Estructura de directorios
- ✅ `package.json`: dependencias (React, TanStack Query/Table, Axios)
- ✅ `vite.config.ts`: configuración de Vite
- ✅ `tsconfig.json`: configuración TypeScript
- ✅ `tailwind.config.js`: configuración Tailwind CSS
- ✅ `App.tsx`: componente raíz con Router
- ✅ `Dockerfile.dev`: imagen para desarrollo
- ⏳ Componentes UI (próximo)
- ⏳ Páginas (login, tablero, clientes, etc.)

### 3. Base de datos
- ✅ `docker/postgres/init.sql`: DDL completo con:
  - Tablas maestras (clientes, productos)
  - Dominio comercial (ventas, líneas, cuotas, pagos)
  - RBAC (usuarios, roles, permisos)
  - Auditoría
  - RAG (documentos, chunks con pgvector)
  - Parámetros de negocio

### 4. Orquestación
- ✅ `docker-compose.yml`: servicios (postgres, api, frontend)
- ✅ `.env.example`: variables de entorno

## Próximos pasos (Fase 1)

1. **Modelos SQLAlchemy** → `backend/app/models.py`
   - Mapeo ORM de todas las tablas del DDL

2. **Esquemas Pydantic** → `backend/app/schemas/`
   - DTOs para request/response (clientes, productos, ventas, etc.)

3. **Rutas API** → `backend/app/routers/`
   - POST/GET/PUT/DELETE para maestros
   - Lógica de ventas con cálculo de cuotas
   - Pagos en cascada
   - Autenticación (JWT)

4. **Páginas React** → `frontend/src/pages/`
   - Login
   - Tablero (KPIs)
   - Clientes (CRUD)
   - Productos (CRUD)
   - Ventas (creación, detalle, anulación)
   - Cobranza (pagos, prorrogas)

5. **Migraciones** → `migrations/` (Alembic)
   - Versionado de cambios al schema

6. **Autenticación y RBAC**
   - JWT + refresh tokens
   - Middleware de permisos
   - Gestión de usuarios/roles

## Cómo ejecutar

### Desarrollo local con Docker Compose

```bash
# Crear .env desde .env.example
cp .env.example .env

# Iniciar servicios
docker-compose up -d

# Frontend estará en http://localhost:5173
# API estará en http://localhost:8000
# Docs en http://localhost:8000/docs
```

### Desarrollo manual (sin Docker)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

## Configuración

Las variables de entorno en `.env`:
- `DB_USER`, `DB_PASSWORD`, `DB_NAME` → PostgreSQL
- `JWT_SECRET_KEY` → Clave para tokens JWT
- `IVA_PCT`, `MORA_PCT_MENSUAL`, etc. → Parámetros de negocio

Ver `.env.example` para todos los valores por defecto.

## Decisiones documentadas

- **Base de cobranza (D-1):** Total con IVA (configurado en `parametros` como `BASE_COBRANZA=TOTAL`)
- **Backend (D-2):** FastAPI (afinidad RAG/MCP, código limpio)
- **Auth:** JWT access + refresh (implementar en Fase 1)
- **RBAC:** Roles iniciales (admin, vendedor, cobranza, lectura)

## Referencias

- Diseño completo: [SDD_Mini-ERP_CNA.md](SDD_Mini-ERP_CNA.md)
- Historial: [BITACORA.md](BITACORA.md)
- Instrucciones: [CLAUDE.md](CLAUDE.md)
