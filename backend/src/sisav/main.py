from fastapi import FastAPI

from sisav.core.config import get_settings
from sisav.api.academico import router as academico_router

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

# 2. Registe o router na aplicação
app.include_router(academico_router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}