from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, cliente, producto, venta, cobranza, tablero

settings = get_settings()

app = FastAPI(
    title="Mini-ERP Comercial CNA",
    description="Sistema de gestión de ventas de fertilizantes",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(cliente.router)
app.include_router(producto.router)
app.include_router(venta.router)
app.include_router(cobranza.router)
app.include_router(tablero.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}

@app.get("/")
def root():
    return {
        "message": "Mini-ERP Comercial CNA API",
        "version": "0.1.0",
        "docs": "/docs",
    }
