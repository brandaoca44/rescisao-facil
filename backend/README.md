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

Datas usam `AAAA-MM-DD`. Os valores monetários de entrada aceitam até dez dígitos inteiros e duas casas decimais. O salário deve ser positivo e a base do FGTS não pode ser negativa. As quantidades de férias têm zero como padrão e devem ser compatíveis com o vínculo.

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
  "total": "22850.00",
  "net_total": "22516.12"
}
```

Esse trecho é um recorte da resposta. `total` soma as verbas de pagamento direto e `net_total` desconta INSS, IRRF e eventual aviso não cumprido. Depósitos e multa do FGTS ficam separados desses totais.

### Erros

- **400:** inconsistência de domínio, como desligamento anterior à admissão, férias incompatíveis ou combinação de aviso inválida.
- **422:** entrada inválida ou ano tributário não suportado. As tabelas atuais atendem desligamentos em 2026.

## Premissas e limitações

O cálculo adota as [premissas documentadas](../docs/calculation-rules.md), incluindo a convenção de 30 dias para saldo salarial. A API não reconstrói histórico de férias ou depósitos do FGTS. Dependentes, pensão alimentícia e previdência complementar não são integralmente contemplados. Informações sobre saque do FGTS e seguro-desemprego ainda não estão disponíveis.
