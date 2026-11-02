from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.terminations import router as terminations_router


app = FastAPI(
    title="Rescisão Fácil API",
    version="0.1.0",
    description=(
        "API para estimar rescisões trabalhistas nas quatro modalidades suportadas. "
        "Os valores são apresentados em reais, com verbas, descontos e FGTS "
        "separados. As tabelas tributárias disponíveis correspondem a 2026. "
        "Consulte os exemplos e as condições dos campos antes do cálculo."
    ),
)

app.include_router(health_router)
app.include_router(terminations_router)