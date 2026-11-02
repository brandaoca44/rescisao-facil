from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from app.schemas.errors import CalculationValidationErrorResult, DomainErrorResult

from app.schemas.termination import (
    TerminationCalculationInput,
    TerminationCalculationResult,
)
from app.services.termination_service import calculate_termination


REQUEST_EXAMPLES = {'dismissal_without_cause': {'summary': 'Dispensa sem justa causa com aviso indenizado',
                             'value': {'monthly_salary': '3000.00',
                                       'admission_date': '2024-01-10',
                                       'termination_date': '2026-08-20',
                                       'acquired_vacation_periods': 1,
                                       'overdue_vacation_periods': 1,
                                       'fgts_rescission_base': '10000.00',
                                       'termination_type': 'dismissal_without_cause',
                                       'notice_period_type': 'indemnified'}},
 'resignation': {'summary': 'Pedido de demissão com aviso não cumprido',
                 'value': {'monthly_salary': '3000.00',
                           'admission_date': '2024-01-10',
                           'termination_date': '2026-08-20',
                           'acquired_vacation_periods': 1,
                           'overdue_vacation_periods': 1,
                           'fgts_rescission_base': '10000.00',
                           'termination_type': 'resignation',
                           'notice_period_type': 'not_worked'}},
 'mutual_agreement': {'summary': 'Acordo com aviso indenizado',
                      'value': {'monthly_salary': '3000.00',
                                'admission_date': '2024-01-10',
                                'termination_date': '2026-08-20',
                                'acquired_vacation_periods': 1,
                                'overdue_vacation_periods': 1,
                                'fgts_rescission_base': '10000.00',
                                'termination_type': 'mutual_agreement',
                                'notice_period_type': 'indemnified'}},
 'dismissal_with_cause': {'summary': 'Justa causa, sem aviso',
                          'value': {'monthly_salary': '3000.00',
                                    'admission_date': '2024-01-10',
                                    'termination_date': '2026-08-20',
                                    'acquired_vacation_periods': 1,
                                    'overdue_vacation_periods': 1,
                                    'fgts_rescission_base': '10000.00',
                                    'termination_type': 'dismissal_with_cause'}},
 'worked_notice': {'summary': 'Pedido de demissão com aviso trabalhado',
                   'value': {'monthly_salary': '3000.00',
                             'admission_date': '2024-01-10',
                             'termination_date': '2026-08-20',
                             'acquired_vacation_periods': 1,
                             'overdue_vacation_periods': 1,
                             'fgts_rescission_base': '10000.00',
                             'termination_type': 'resignation',
                             'notice_period_type': 'worked'}},
 'year_boundary_with_previous_payment': {'summary': 'Projeção para janeiro e décimo terceiro '
                                                    'anterior quitado',
                                         'value': {'monthly_salary': '3000.00',
                                                   'admission_date': '2024-01-10',
                                                   'termination_date': '2026-12-20',
                                                   'acquired_vacation_periods': 1,
                                                   'overdue_vacation_periods': 0,
                                                   'fgts_rescission_base': '10000.00',
                                                   'termination_type': 'dismissal_without_cause',
                                                   'notice_period_type': 'indemnified',
                                                   'thirteenth_previous_payment': {'gross_amount': '3000.00',
                                                                                   'inss_withheld': '248.60',
                                                                                   'irrf_withheld': '0.00',
                                                                                   'fgts_deposited': '240.00'}}}}

SUCCESS_EXAMPLE = {'salary_balance': '2000.00',
 'thirteenth_salary': '2250.00',
 'thirteenth_salary_by_year': [{'year': 2026, 'accrued_months': 9, 'value': '2250.00'}],
 'thirteenth_settlement': {'gross_paid': '0.00',
                           'gross_balance': '2250.00',
                           'inss_assessed': '178.19',
                           'irrf_assessed': '0.00',
                           'inss_previously_withheld': '0.00',
                           'irrf_previously_withheld': '0.00',
                           'fgts_previously_deposited': '0.00'},
 'vacation_accrued_months': 9,
 'proportional_vacation': '2250.00',
 'proportional_vacation_bonus': '750.00',
 'acquired_vacation': '3000.00',
 'acquired_vacation_bonus': '1000.00',
 'overdue_vacation': '6000.00',
 'overdue_vacation_bonus': '2000.00',
 'notice_period_days': 36,
 'notice_period_value': '3600.00',
 'notice_period_discount': '0.00',
 'projected_termination_date': '2026-09-25',
 'fgts_termination_deposit': '628.00',
 'fgts_penalty': '4000.00',
 'inss_monthly': '155.69',
 'inss_thirteenth': '178.19',
 'inss_total': '333.88',
 'irrf_monthly': '0.00',
 'irrf_thirteenth': '0.00',
 'irrf_total': '0.00',
 'total': '22850.00',
 'net_total': '22516.12',
 'benefits': {'fgts_withdrawal_rate_under_saque_rescisao': '1.00',
              'unemployment_insurance_possible_by_termination_type': True,
              'notes': ['O percentual de saque pressupõe a sistemática saque-rescisão e não '
                        'confirma saldo disponível ou liberação imediata.',
                        'Na sistemática saque-aniversário, a regra geral para este desligamento '
                        'permite sacar a multa rescisória, sem liberar o restante do saldo por '
                        'esse motivo. Regras extraordinárias e restrições da conta exigem '
                        'verificação específica.',
                        'A concessão do seguro-desemprego depende dos demais requisitos legais, '
                        'incluindo histórico salarial, solicitações anteriores, situação de '
                        'desemprego, renda e benefícios recebidos.']}}

router = APIRouter(
    prefix="/api/v1/terminations",
    tags=["Terminations"],
)


@router.post(
    "/calculate",
    response_model=TerminationCalculationResult,
    status_code=status.HTTP_200_OK,
    summary="Calcular rescisão trabalhista",
    response_description="Verbas, descontos, totais e direitos informativos do cenário.",
    responses={
        200: {"content": {"application/json": {"example": SUCCESS_EXAMPLE}}},
        400: {
            "model": DomainErrorResult,
            "description": "Datas, férias, aviso ou histórico de décimo terceiro incompatíveis.",
            "content": {"application/json": {"example": {
                "detail": "Notice period type is not allowed for this termination type.",
            }}},
        },
        422: {
            "model": CalculationValidationErrorResult,
            "description": "Entrada inválida ou tabelas do ano não suportadas.",
            "content": {"application/json": {"examples": {
                "unsupported_year": {"value": {
                    "detail": "Termination calculation tables for 2027 are not supported.",
                }},
                "invalid_input": {"value": {"detail": [{
                    "type": "greater_than", "loc": ["body", "monthly_salary"],
                    "msg": "Input should be greater than 0", "input": "0.00",
                    "ctx": {"gt": 0},
                }]}},
            }}},
        },
    },
)
def calculate_termination_endpoint(
    data: Annotated[TerminationCalculationInput, Body(openapi_examples=REQUEST_EXAMPLES)],
) -> TerminationCalculationResult:
    """Estima a rescisão para uma das quatro modalidades suportadas.

    Valores monetários retornam como strings decimais em reais. FGTS e multa
    ficam separados do bruto e do líquido. Os direitos informativos não
    confirmam saldo disponível ou concessão de benefício. O ano tributário
    suportado é 2026; a projeção do aviso não habilita tabelas de outro ano.
    """

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