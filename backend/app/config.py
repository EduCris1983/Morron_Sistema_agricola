from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/morron_erp"
    JWT_SECRET_KEY: str = "change-me-in-production"
    ENVIRONMENT: str = "development"

    # Parámetros de negocio
    IVA_PCT: float = 0.19
    MORA_PCT_MENSUAL: float = 0.01
    DIAS_POR_MES: int = 30
    BASE_COBRANZA: str = "TOTAL"  # NETO | TOTAL (D-1 confirmado: TOTAL)

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
