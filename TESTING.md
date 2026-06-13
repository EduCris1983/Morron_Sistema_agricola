# Testing — Mini-ERP Comercial CNA

## 🚀 Cómo ejecutar la aplicación

### Requisitos
- Docker Desktop instalado
- Git (para clonar el repo)
- 4GB RAM libre mínimo

### Pasos 1-2 minutos

```bash
# 1. Clonar o entrar al directorio
cd f:\Proyectos\Morron_sistrema_agricola

# 2. Crear .env desde ejemplo
copy .env.example .env

# 3. (Opcional) Ajustar variables si deseas (default funcionan bien)
# Defaults:
#   DB_USER=postgres, DB_PASSWORD=postgres
#   API_PORT=8000, FRONTEND_PORT=5173

# 4. Levantar servicios
docker-compose up

# Esperar 30-60 segundos hasta ver:
# - "postgres | ready to accept connections"
# - "morron_api | Uvicorn running on http://0.0.0.0:8000"
# - "morron_frontend | ✓ ready in XXXms"
```

---

## 🌐 URLs de acceso

| Servicio | URL |
|----------|-----|
| **Frontend (React)** | http://localhost:5175 |
| **API (FastAPI)** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API ReDoc** | http://localhost:8000/redoc |
| **PostgreSQL** | localhost:5432 (usuario: postgres, password: postgres) |

---

## 👤 Credenciales de prueba

**Nota:** Los usuarios se crean automáticamente. Para crear el primer usuario, usa el endpoint `POST /auth/registro`:

### Crear usuario de prueba (desde Swagger)

1. Abre http://localhost:8000/docs
2. Busca `POST /auth/registro`
3. Expande y haz clic en "Try it out"
4. Ingresa:
```json
{
  "email": "admin@cna.cl",
  "nombre": "Administrador",
  "password": "admin123"
}
```
5. Ejecuta

### Login

1. Abre http://localhost:5173
2. Email: `admin@cna.cl`
3. Contraseña: `admin123`
4. Presiona "Iniciar sesión"

---

## ✅ Flujo de testing recomendado

### 1. Autenticación (2 min)
- [ ] Ir a http://localhost:5175
- [ ] Ver formulario de login
- [ ] Intentar login con credenciales incorrectas → debe fallar
- [ ] Hacer login con `admin@cna.cl` / `admin123` → debe redirigir a /tablero
- [ ] Ver sidebar con navegación
- [ ] Hacer logout → debe ir a login

### 2. Tablero (1 min)
- [ ] Ver página `/tablero`
- [ ] Verificar KPIs: Margen, CxC, Cuotas vencidas, Ingresos
- [ ] Ver tabla "Top 5 Deudores" (vacía inicialmente)

### 3. Maestros (5 min)

**Crear Cliente:**
- [ ] Ir a `/clientes`
- [ ] Clic "Nuevo Cliente"
- [ ] Ingresar:
  - Razón Social: `Agrícola Sur Ltda.`
  - RUT: `12.345.678-9`
  - Giro: `Agricultura`
  - Email: `contacto@agricolasur.cl`
  - Teléfono: `227654321`
- [ ] Guardar → debe aparecer en tabla
- [ ] Verificar que puede editar

**Crear Productos:**
- [ ] Ir a `/productos`
- [ ] Clic "Nuevo Producto"
- [ ] Crear 2-3 productos (ej):
  - **Producto 1:** Nombre: `Fertilizante NPK 15-15-15`
    - Formulación: `15-15-15`
    - Unidad: `KG`
    - Costo: `50000`
    - Precio: `75000`
  - **Producto 2:** Nombre: `Bioestimulante Líquido`
    - Unidad: `LTS`
    - Costo: `25000`
    - Precio: `40000`
- [ ] Verificar tabla muestra margen (precio - costo)

### 4. Ventas (10 min)

**Crear Venta:**
- [ ] Ir a `/ventas`
- [ ] Clic "Nueva Venta"
- [ ] Formulario:
  - Cliente: `Agrícola Sur Ltda.`
  - Fecha Emisión: hoy
  - Plazo (días): `0`
  - Número de Cuotas: `2`
- [ ] Agregar 2 líneas:
  - Línea 1: Fertilizante NPK × 100 kg @ $75.000
  - Línea 2: Bioestimulante × 50 lts @ $40.000
- [ ] Ver cálculo automático:
  - Subtotal línea 1: $7.500.000
  - Subtotal línea 2: $2.000.000
  - **Neto: $9.500.000**
  - **IVA (19%): $1.805.000**
  - **Total: $11.305.000**
- [ ] Guardar → debe aparecer en listado con estado `VIGENTE`
- [ ] Verificar que en `/tablero` cambió el CxC (ahora debe mostrar $11.305.000)

### 5. Cobranza (10 min)

**Registrar Pago:**
- [ ] Ir a `/cobranza`
- [ ] Seleccionar cliente `Agrícola Sur Ltda.`
- [ ] Verificar estado de cuenta:
  - Total Adeudado: $11.305.000
  - 2 cuotas de $5.652.500 cada una
- [ ] Clic "Registrar Pago"
- [ ] Ingresar:
  - Venta: (la que creamos)
  - Monto: `3.000.000` (pago parcial)
  - Fecha: hoy
  - Medio: `transferencia`
- [ ] Guardar → debe actualizar estado
- [ ] Verificar:
  - Cuota 1 ahora en estado `PARCIAL`
  - Total Adeudado: `$8.305.000`
  - Una cuota sin pago, otra parcialmente pagada

### 6. Admin (5 min) - **Avanzado, solo si tienes curiosidad**

- [ ] Abre Swagger: http://localhost:8000/docs
- [ ] Busca `/admin/usuarios`
- [ ] Clic "Try it out" → Ejecutar
- [ ] Deberías ver tu usuario `admin@cna.cl`

---

## 🐛 Troubleshooting

### "Connection refused" en http://localhost:5175
**Solución:** Espera 1-2 minutos más mientras se construyen las imágenes. Revisa logs: `docker-compose logs frontend`

### "Database connection error" en la API
**Solución:** 
```bash
# Verifica que Postgres está corriendo
docker-compose logs postgres

# Si falla, limpia y reinicia
docker-compose down -v
docker-compose up
```

### Usuario no puede loguearse
**Solución:** 
1. Crea un usuario nuevo vía Swagger en http://localhost:8000/docs
2. POST /auth/registro con tus datos
3. Intenta login con ese usuario

### Frontend no carga
```bash
# Reinstala dependencias
docker-compose down
docker-compose up --build
```

---

## 📝 Datos de prueba listos

**El script `docker/postgres/init.sql` crea automáticamente:**
- ✅ 14 tablas
- ✅ 4 roles (admin, vendedor, cobranza, lectura)
- ✅ 17 permisos granulares
- ✅ Parámetros de negocio (IVA=19%, mora=1% mensual)

---

## 📊 KPIs que deberías ver

Después de crear una venta y un pago:

```
Tablero:
  Margen Acumulado: $1.500.000 (2.000.000 - 500.000)
  CxC Vigente: $8.305.000 (saldo después del pago)
  Cuotas Vencidas: 0 (si el plazo es 0)
  Ingresos Período: $3.000.000 (el pago realizado)
  Top 5 Deudores: "Agrícola Sur Ltda." - $8.305.000
```

---

## ⚠️ Notas importantes

- **Los datos se persisten en volumen Docker** (`postgres_data`) → si ejecutas `docker-compose down`, los datos se mantienen
- **Para limpiar todo:** `docker-compose down -v` (elimina volúmenes)
- **Logs en tiempo real:** `docker-compose logs -f` (y `-f` para API: `docker-compose logs -f api`)
- **Cambios en código:** Haz cambios, guarda, y los contenedores detectan los cambios automáticamente en desarrollo

---

## 🎯 Comandos útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Logs solo de la API
docker-compose logs -f api

# Reiniciar servicios
docker-compose restart

# Detener sin eliminar datos
docker-compose stop

# Reanudar
docker-compose start

# Limpiar todo (incluyendo datos)
docker-compose down -v

# Ejecutar comando en contenedor
docker-compose exec api bash
docker-compose exec postgres psql -U postgres -d morron_erp
```

---

## ✅ Testing completado cuando puedas:

- [ ] Crear cliente
- [ ] Crear productos
- [ ] Crear venta con múltiples líneas
- [ ] Ver cálculo automático de neto/IVA/total
- [ ] Crear cuotas (verlas en cobranza)
- [ ] Registrar pago
- [ ] Ver actualización en tablero KPIs

**Aprox. tiempo total: 30 minutos**

---

---

## 🚀 Listo para testear

Ejecuta en la terminal:
```bash
cd f:\Proyectos\Morron_sistrema_agricola
docker-compose up
```

Luego abre en tu navegador:
- **Frontend:** http://localhost:5175
- **API Docs:** http://localhost:8000/docs

**¿Problemas?** Abre una issue o revisa los logs con `docker-compose logs`

**Repositorio:** https://github.com/EduCris1983/Morron_Sistema_agricola
