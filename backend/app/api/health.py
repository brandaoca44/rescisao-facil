from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Verifica se a API está disponível."""
    return {"status": "ok"}
