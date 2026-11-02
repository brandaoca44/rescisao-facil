# Backend — Rescisão Fácil

API de cálculo de rescisão trabalhista desenvolvida em Python 3.14 com FastAPI. As regras ficam em `app/domain`, a orquestração em `app/services`, os contratos em `app/schemas` e os endpoints em `app/api`.

## Executar

Com Python 3.14 instalado, execute a partir da raiz do repositório:

```powershell
cd backend
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Os comandos acima usam PowerShell. O manifesto inclui dependências de execução e testes com versões fixadas. O servidor de desenvolvimento disponibiliza a documentação em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Testes

Dentro de `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

A suíte cobre cálculos isolados, validações, orquestração e respostas HTTP, incluindo datas de fronteira, valores monetários e combinações de aviso prévio.

### Integração contínua

O workflow [Backend CI](../.github/workflows/backend-ci.yml) executa a instalação das dependências, `pip check` e a suíte em pushes e pull requests. Usa Python 3.14 em Ubuntu 24.04, com cache do pip baseado em `requirements.txt`. Avisos durante os testes são tratados como falhas.

O resultado fica na aba Actions do GitHub e nas verificações do pull request. A execução também pode ser iniciada manualmente pela aba Actions após o workflow estar na branch padrão. Novos commits cancelam execuções anteriores do mesmo contexto.

Antes de enviar uma alteração, execute dentro de `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest -q -W error -p no:cacheprovider
```

As ações oficiais são fixadas por commit e o workflow usa acesso de leitura ao repositório, sem precisar de segredos adicionais. O CI verifica o backend; não realiza deploy. A exigência de aprovação desse check para merge depende da proteção de branches configurada no GitHub.

## Endpoints

| Método | Caminho | Finalidade |
| --- | --- | --- |
| GET | `/health` | Verificar a disponibilidade da API |
| POST | `/api/v1/terminations/calculate` | Calcular a rescisão |
| GET | `/docs` | Consultar e testar o contrato no Swagger |
| GET | `/openapi.json` | Obter a especificação OpenAPI |

### Exemplo de requisição

Envie o corpo abaixo ao endpoint de cálculo com `Content-Type: application/json`:

```json
{
  "monthly_salary": "3000.00",
  "admission_date": "2024-01-10",
  "termination_date": "2026-08-20",
  "termination_type": "dismissal_without_cause",
  "notice_period_type": "indemnified",
  "acquired_vacation_periods": 1,
  "overdue_vacation_periods": 1,
  "fgts_rescission_base": "10000.00"
}
```

O Swagger oferece exemplos executáveis das quatro modalidades, aviso trabalhado e virada do ano com décimo terceiro anterior. A resposta de sucesso documentada corresponde a um cálculo completo.

Datas usam `AAAA-MM-DD`. Os valores monetários de entrada aceitam até dez dígitos inteiros e duas casas decimais. O salário deve ser positivo e a base do FGTS não pode ser negativa. As quantidades de férias têm zero como padrão e devem ser compatíveis com o vínculo. Campos desconhecidos no corpo da requisição ou no histórico de décimo terceiro são rejeitados com HTTP 422.

No aviso trabalhado, `termination_date` representa o último dia de cumprimento. No aviso indenizado, representa o desligamento efetivo antes da projeção calculada pelo motor.

`fgts_rescission_base` representa a base informada para calcular a multa. Não deve ser interpretada como saldo disponível para saque.

### Modalidade e aviso

| `termination_type` | Situações explícitas de `notice_period_type` |
| --- | --- |
| `dismissal_without_cause` | `worked`, `indemnified` |
| `resignation` | `worked`, `not_worked` |
| `mutual_agreement` | `worked`, `indemnified` |
| `dismissal_with_cause` | Nenhuma; omitir o campo ou usar `null` |

O campo de aviso é opcional para compatibilidade. Quando omitido, sem justa causa e acordo aplicam o comportamento indenizado existente; pedido de demissão não aplica desconto de aviso; justa causa não gera aviso. Para informar descumprimento no pedido de demissão, use `not_worked`.

### Resposta

A resposta detalha saldo de salário, décimo terceiro, férias e adicionais, aviso, FGTS, INSS e IRRF. Valores monetários são serializados como strings decimais. O Swagger apresenta o schema completo.

No exemplo acima, alguns campos retornados são:

```json
{
  "salary_balance": "2000.00",
  "notice_period_days": 36,
  "notice_period_value": "3600.00",
  "notice_period_discount": "0.00",
  "projected_termination_date": "2026-09-25",
  "fgts_penalty": "4000.00",
  "thirteenth_salary_by_year": [
    {"year": 2026, "accrued_months": 9, "value": "2250.00"}
  ],
  "total": "22850.00",
  "net_total": "22516.12"
}
```

Esse trecho é um recorte da resposta. `total` soma as verbas de pagamento direto e `net_total` desconta as retenções adicionais de INSS e IRRF, eventual aviso não cumprido e o décimo terceiro bruto já pago informado. Depósitos e multa do FGTS ficam separados desses totais.

### Décimo terceiro por ano

`thirteenth_salary_by_year` detalha os avos e valores do ano do desligamento até o fim da projeção do aviso. A soma dos valores corresponde a `thirteenth_salary`. A projeção não elimina os avos do ano anterior e cada ano tem no máximo 12 avos.

Exemplo: com salário de R$ 3.000, vínculo iniciado em 10/01/2024, desligamento em 20/12/2026 e aviso indenizado de 36 dias, a projeção vai até 25/01/2027. O detalhamento contém R$ 3.000 para 2026 e R$ 250 para 2027, somando R$ 3.250. Na justa causa, o detalhamento é vazio.

São valores brutos antes dos abatimentos informados em `thirteenth_previous_payment`. A projeção em 2027 não habilita desligamentos ou pagamentos tributados por tabelas de 2027.

### Décimo terceiro já pago

O objeto opcional `thirteenth_previous_payment` informa exclusivamente o histórico do décimo terceiro do ano do desligamento. Todos os valores têm zero como padrão:

```json
{
  "thirteenth_previous_payment": {
    "gross_amount": "3000.00",
    "inss_withheld": "248.60",
    "irrf_withheld": "0.00",
    "fgts_deposited": "240.00"
  }
}
```

Esse é um complemento ao corpo da requisição. `gross_amount` é o valor bruto, antes dos descontos; os outros campos representam retenções efetivas do empregado e FGTS efetivamente depositado sobre o mesmo décimo terceiro. Não informar o líquido como bruto, contribuições patronais ou valores de outras verbas. Omitir o objeto preserva o cálculo sem histórico.

A resposta `thirteenth_settlement` apresenta o bruto já pago, o saldo bruto, os tributos integrais apurados e as retenções anteriores compensadas. `inss_thirteenth` e `irrf_thirteenth` representam apenas o adicional a reter agora. A base dos tributos continua sendo o décimo terceiro integral. O depósito rescisório de FGTS é reduzido pelo FGTS anterior informado, sem alterar a multa.

O bruto integral permanece em `thirteenth_salary` e `total`; o pagamento anterior é abatido uma única vez em `net_total`:

```text
net_total = total - inss_total - irrf_total
            - notice_period_discount - thirteenth_settlement.gross_paid
```

Na projeção de dezembro para janeiro, pagamentos do ano do desligamento não podem consumir a parcela do ano seguinte. Pagamentos acima do devido, retenções superiores ao imposto recalculado e FGTS que exigiria restituição retornam HTTP 400. A V1 não calcula recuperação de adiantamentos excedentes ou restituições. Campos desconhecidos no objeto de histórico retornam HTTP 422.

### Férias

As quantidades de férias integrais representam períodos não quitados na data projetada do desligamento: `acquired_vacation_periods` para períodos simples e `overdue_vacation_periods` para períodos com prazo concessivo encerrado. Os campos devem incluir os períodos completados pela projeção, sem repetição entre as duas categorias. O motor valida os limites possíveis e calcula separadamente as férias proporcionais do período incompleto.

As [regras de férias](../docs/vacation-rules.md) detalham a contagem para admissões nos dias 29, 30 e 31, as fronteiras do prazo concessivo e as limitações do histórico informado.

### Direitos informativos

A resposta inclui `benefits`, sem novos campos de entrada. Exemplo na dispensa sem justa causa:

```json
{
  "benefits": {
    "fgts_withdrawal_rate_under_saque_rescisao": "1.00",
    "unemployment_insurance_possible_by_termination_type": true,
    "notes": [
      "O percentual de saque pressupõe a sistemática saque-rescisão e não confirma saldo disponível ou liberação imediata.",
      "Na sistemática saque-aniversário, a regra geral para este desligamento permite sacar a multa rescisória, sem liberar o restante do saldo por esse motivo. Regras extraordinárias e restrições da conta exigem verificação específica.",
      "A concessão do seguro-desemprego depende dos demais requisitos legais, incluindo histórico salarial, solicitações anteriores, situação de desemprego, renda e benefícios recebidos."
    ]
  }
}
```

O percentual é uma fração entre zero e um: `1.00` significa 100% e `0.80`, 80%. Ele descreve a regra do desligamento na sistemática saque-rescisão; não é valor monetário nem confirmação de disponibilidade. O indicador do seguro-desemprego avalia somente a modalidade, sem confirmar o cumprimento dos requisitos individuais. As notas devem acompanhar a apresentação dessas informações.

O objeto não altera os totais, não calcula o saldo a sacar e não estima valores ou parcelas do seguro-desemprego.

### Erros

- **400:** inconsistência de domínio, como desligamento anterior à admissão, férias incompatíveis ou combinação de aviso inválida.
- **422:** entrada inválida ou ano tributário não suportado. As tabelas atuais atendem desligamentos em 2026.

Erros de domínio e funcionalidades não suportadas usam uma mensagem em `detail`:

```json
{"detail": "Notice period type is not allowed for this termination type."}
```

Erros de validação de entrada usam uma lista em `detail`, com `loc` para identificar o campo, `type` para classificar o erro e `msg` para descrevê-lo. Também podem incluir `input` e `ctx`. Exemplo para salário zero:

```json
{
  "detail": [{
    "type": "greater_than",
    "loc": ["body", "monthly_salary"],
    "msg": "Input should be greater than 0",
    "input": "0.00",
    "ctx": {"gt": 0}
  }]
}
```

O cliente deve aceitar ambos os formatos de HTTP 422. Para relacionar erros de entrada aos campos, use `loc` e `type`, sem depender de comparação textual com `msg`. Os exemplos e schemas de erro estão disponíveis no Swagger.

O contrato usa valores monetários decimais em texto na resposta. `total` é o bruto integral antes das compensações; `net_total` inclui os abatimentos e pode ser negativo se os descontos superarem as verbas. Um saldo negativo não constitui, por si, autorização de cobrança.

## Premissas e limitações

As [regras tributárias de 2026](../docs/tax-rules.md) detalham as bases, a dispensa de retenção mensal até R$ 10, o tratamento do décimo terceiro e as limitações de agregação de pagamentos.

O cálculo adota as [premissas documentadas](../docs/calculation-rules.md), incluindo a convenção de 30 dias para saldo salarial. A API não reconstrói histórico de férias ou depósitos do FGTS. Dependentes, pensão alimentícia e previdência complementar não são integralmente contemplados. Os direitos informativos não avaliam a sistemática individual de saque, bloqueios da conta ou os requisitos pessoais de concessão do seguro-desemprego.

## Aceite da V1

O [registro de aceite técnico](../docs/backend-v1-acceptance.md) reúne o escopo verificado, as evidências e as limitações para integração. O fechamento do checkpoint exige que os ajustes estejam versionados e aprovados pelo CI no mesmo commit.
