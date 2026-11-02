# Aceite técnico do backend V1

## Resultado

O backend atende aos critérios técnicos de integração dentro do escopo descrito neste documento. A revisão executou 378 testes com avisos tratados como erros, sem falhas, e a verificação de dependências não encontrou incompatibilidades.

O fechamento do checkpoint versionado permanece pendente até o commit dos últimos ajustes de contrato e uma execução aprovada do CI sobre esse mesmo commit. A execução anterior do CI não substitui essa confirmação.

Este aceite não amplia o escopo do motor nem representa certificação de cálculo trabalhista ou fiscal definitivo.

## Escopo aceito

- Estimativa de contrato CLT mensalista com salário fixo, nas quatro modalidades implementadas.
- Desligamento efetivo em 2026; a projeção do aviso pode alcançar o ano seguinte sem habilitar tabelas tributárias futuras.
- Saldo salarial pela convenção de 30 dias documentada.
- Décimo terceiro proporcional por ano, com compensação de pagamentos, retenções e FGTS anteriores informados para o ano do desligamento.
- Férias proporcionais e períodos integrais simples ou vencidos, conforme as quantidades informadas na data projetada.
- Aviso trabalhado, indenizado ou não cumprido, nas combinações permitidas, com compatibilidade para o campo omitido.
- FGTS, multa, INSS, IRRF, bruto integral, líquido e direitos informativos separados.

## Critérios verificados

| Área | Resultado | Evidência principal |
| --- | --- | --- |
| Quatro modalidades e aviso | Conforme | `test_termination_rules.py`, `test_notice_period_rules.py`, `test_termination_regressions.py` |
| Datas, dias trabalhados e ano bissexto | Conforme no modelo | `test_salary_balance.py`, `test_notice_period.py`, `test_termination_regressions.py` |
| Décimo terceiro entre anos | Conforme | `test_thirteenth_year_boundary.py` |
| Pagamentos e retenções anteriores | Conforme no escopo suportado | `test_thirteenth_settlement.py`, `test_thirteenth_previous_payment_api.py` |
| Férias e fronteiras do calendário | Conforme no modelo | `test_vacation.py`, `test_vacation_calendar_audit.py` |
| FGTS e multa separados do pagamento direto | Conforme | `test_fgts.py`, `test_termination_service.py` |
| Tributos de 2026 e retenção adicional | Conforme no escopo suportado | `test_inss.py`, `test_irrf.py`, `test_tax_audit.py` |
| Direitos informativos condicionais | Conforme | `test_termination_benefits.py`, `test_termination_benefits_integration.py` |
| Contrato, exemplos e erros HTTP | Conforme | `test_api_contract.py` |
| Dependências e execução dos testes | Conforme localmente | `requirements.txt`, `pip check` e suíte completa |
| CI do checkpoint final | Pendente de consolidação | `.github/workflows/backend-ci.yml` |

Os arquivos de teste estão em [backend/tests](../backend/tests). Os exemplos publicados no OpenAPI são executados pelos testes de contrato; a resposta de sucesso documentada é comparada à resposta real. Os testes verificam os formatos de erro 400 e 422, a rejeição de campos desconhecidos, a serialização decimal e a disponibilidade de `/docs`, `/openapi.json` e `/health`.

## Limitações assumidas

| Situação | Tratamento da V1 |
| --- | --- |
| Anos tributários diferentes de 2026 | Rejeitados explicitamente |
| Dados inválidos ou campos desconhecidos | HTTP 422 |
| Datas, aviso, férias ou histórico incompatíveis | HTTP 400 |
| Adiantamento do décimo terceiro acima do devido ou valores que exigem restituição | Rejeitados; recuperação e devolução não são simuladas |
| Histórico de férias e afastamentos | Não reconstruído; informar períodos integrais pendentes, incluindo os completados pela projeção |
| Férias parcialmente gozadas, dobra parcial, faltas e perda ou reinício de período | Não modelados |
| Aviso parcialmente cumprido, dispensa de cumprimento ou aviso misto | Não modelados; não substituir por uma situação aproximada |
| Remuneração variável, adicionais e particularidades de convenção coletiva | Não modelados |
| Dependentes, pensão, previdência complementar e vínculos concomitantes | Não integralmente contemplados |
| Outros pagamentos mensais e imposto mensal já retido | Não agregados; o histórico compensável é específico do décimo terceiro |
| Quitação em outra data, diferenças de competência e rendimentos acumulados de anos anteriores | Não modelados |
| Saque efetivo do FGTS e concessão do seguro-desemprego | Não confirmados; retorno apenas informativo por modalidade |

As convenções de saldo salarial e de projeção do acordo permanecem registradas nas [premissas](calculation-rules.md). As limitações não devem ser ocultadas pela futura interface. Um total líquido negativo não representa autorização automática de cobrança.

## Contrato para integração

O endpoint é `POST /api/v1/terminations/calculate`. Valores monetários retornam como strings decimais em reais. `total` é o bruto integral; `net_total` desconta as retenções adicionais, o aviso não cumprido e o décimo terceiro bruto já pago informado. FGTS e multa ficam separados desses totais.

O cliente deve usar as descrições e os exemplos do OpenAPI, aceitar os dois formatos de `detail` no HTTP 422 e exibir as condições de `benefits`. As instruções completas estão no [guia do backend](../backend/README.md).

## Fechamento do checkpoint

1. Revisar e versionar os ajustes de contrato e este registro de aceite.
2. Publicar o commit e confirmar sucesso do Backend CI sobre o mesmo SHA.
3. Confirmar que as limitações acima compõem o escopo aprovado da V1 antes de definir a interface.

A preparação do frontend e do deploy deve preservar os serviços existentes. Nenhuma porta, container ou banco de dados é necessário para os testes internos. Se a integração exigir um servidor local ou nova infraestrutura, verificar as portas ocupadas e confirmar a escolha com o responsável antes de iniciar. Não há necessidade validada de autenticação, persistência ou PostgreSQL para o motor atual.
