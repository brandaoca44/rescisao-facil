from typing import Any

from pydantic import BaseModel, Field


class DomainErrorResult(BaseModel):
    detail: str = Field(description="Descrição da inconsistência de domínio.")


class RequestValidationIssue(BaseModel):
    loc: list[str | int]
    msg: str
    type: str
    input: Any = None
    ctx: dict[str, Any] | None = None


class CalculationValidationErrorResult(BaseModel):
    detail: str | list[RequestValidationIssue] = Field(
        description=(
            "Lista de erros para entrada inválida ou mensagem para "
            "funcionalidade ou ano não suportado."
        ),
    )
