# Frontend Mini-ERP Comercial CNA

Aplicación React + TypeScript + Vite para la gestión de ventas de fertilizantes.

## Estructura

```
src/
  pages/           # Páginas principales (Login, Tablero, Clientes, etc.)
  components/      # Componentes reutilizables (Layout, ProtectedRoute)
  services/        # Servicios API (authService, clienteService, etc.)
  lib/             # Utilidades (api.ts - cliente axios)
  App.tsx          # Componente raíz con rutas
  main.tsx         # Punto de entrada
  index.css        # Estilos globales (Tailwind)
```

## Servicios API

- **authService**: Login, refresh token, registro
- **clienteService**: CRUD de clientes
- **productoService**: CRUD de productos
- **ventaService**: Crear ventas, listar, anular
- **cobranzaService**: Pagos, prorrogas, estado de cuenta
- **tableroService**: KPIs, resumen de ventas

## Características implementadas

✅ Login con JWT (access + refresh token)
✅ Tablero con KPIs (margen, CxC, cuotas vencidas, top deudores)
✅ CRUD de Clientes
✅ Rutas protegidas
✅ Logout automático con refresh token expirado
✅ TanStack Query para caché y sincronización de datos

## Páginas

- **Login**: Autenticación con email/contraseña
- **Tablero**: KPIs principales, gráficos de deudores
- **Clientes**: Listado y formulario de clientes
- **Productos**: (próxima)
- **Ventas**: (próxima)
- **Cobranza**: (próxima)

## Variables de entorno

```
VITE_API_BASE_URL=http://localhost:8000
```

## Instalación

```bash
cd frontend
npm install
npm run dev
```

El servidor estará disponible en `http://localhost:5173`.

## Build

```bash
npm run build
```

Genera archivos estáticos en `dist/`.
