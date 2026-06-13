# Migraciones de Base de Datos — Alembic

Versionado de cambios al schema de PostgreSQL usando Alembic.

## Estructura

```
migrations/
  env.py                 # Configuración de Alembic
  script.py.mako         # Template para scripts de migración
  versions/              # Historial de migraciones
    001_initial_schema.py
    002_*.py
    ...
```

## Comandos

### Crear nueva migración (después de cambios en modelos)

```bash
cd backend
alembic revision --autogenerate -m "Descripción del cambio"
```

### Revisar migraciones pendientes

```bash
alembic upgrade --sql
```

### Aplicar migraciones (upgrade)

```bash
alembic upgrade head
```

### Revertir a migración anterior (downgrade)

```bash
alembic downgrade -1
```

### Ver historial de migraciones

```bash
alembic history
```

### Ver versión actual

```bash
alembic current
```

## Configuración

`env.py` carga automáticamente:
- `DATABASE_URL` desde `.env`
- Modelos de `app.models` (Base.metadata)
- Detecta cambios automáticamente con `--autogenerate`

## Flujo de desarrollo

1. Modificar modelos en `app/models.py`
2. Crear migración: `alembic revision --autogenerate -m "descripción"`
3. Revisar archivo generado en `versions/`
4. Aplicar: `alembic upgrade head`
5. Hacer commit de la migración

## Notas

- **Nunca** edites migraciones ya aplicadas en producción
- Las migraciones son ACID (todo-o-nada)
- `downgrade` se usa para development/testing, nunca en producción
- Todas las migraciones son reversibles
