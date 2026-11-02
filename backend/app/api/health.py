from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get(
    "/health", summary="Verificar disponibilidade da API",
    responses={200: {"content": {"application/json": {"example": {"status": "ok"}}}}},
)
def health_check() -> dict[str, str]:
    """Verifica se a API está disponível."""
    return {"status": "ok"}
