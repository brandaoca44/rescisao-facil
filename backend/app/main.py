from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.terminations import router as terminations_router


app = FastAPI(
    title="Rescisão Fácil API",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(terminations_router)