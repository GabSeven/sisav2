from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from sisav.academico.frequencia_router import router as frequencia_router
from sisav.academico.router import router as academico_router
from sisav.auth.router import router as auth_router
from sisav.core.config import get_settings
from sisav.usuarios.router import router as usuarios_router

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(academico_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(frequencia_router, prefix=settings.api_v1_prefix)
app.include_router(usuarios_router, prefix=settings.api_v1_prefix)

settings.upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}