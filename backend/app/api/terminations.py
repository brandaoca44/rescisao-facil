from fastapi import APIRouter, HTTPException, status

from app.schemas.termination import (
    TerminationCalculationInput,
    TerminationCalculationResult,
)
from app.services.termination_service import calculate_termination


router = APIRouter(
    prefix="/api/v1/terminations",
    tags=["Terminations"],
)


@router.post(
    "/calculate",
    response_model=TerminationCalculationResult,
    status_code=status.HTTP_200_OK,
)
def calculate_termination_endpoint(
    data: TerminationCalculationInput,
) -> TerminationCalculationResult:
    """Calcula parcialmente uma rescisão trabalhista suportada pelo motor."""

    try:
        return calculate_termination(data)
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc