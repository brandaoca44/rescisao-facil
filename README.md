# Rescisão Fácil

Aplicação em desenvolvimento para estimar verbas de rescisão trabalhista brasileira, com detalhamento de valores, descontos e premissas do cálculo.

O projeto integra meu portfólio profissional e busca demonstrar modelagem de domínio, desenvolvimento de APIs, testes automatizados e entrega de uma aplicação web completa.

## Estado do projeto

O backend está em desenvolvimento avançado. A V1 ainda depende de auditoria das regras, validações complementares, documentação e estabilização do contrato da API.

O último checkpoint informado é de **124 testes aprovados**. 

Há uma estrutura inicial de Next.js em `frontend/`. A interface do produto e sua integração com a API permanecem pendentes. O backend será concluído antes da evolução funcional do frontend.

Este README descreve o código disponível na árvore de trabalho. Parte das funcionalidades do backend ainda está em alterações locais sem commit; sua consolidação no Git faz parte do roteiro abaixo.

## Tecnologias

- Backend: Python 3.14, FastAPI e Pydantic.
- Cálculos financeiros: `Decimal`.
- Testes: pytest e TestClient.
- Servidor de desenvolvimento: Uvicorn.
- Estrutura inicial do frontend: Next.js, React, TypeScript e Tailwind CSS.

A arquitetura definitiva do frontend e a infraestrutura de publicação serão revisadas antes da implementação. Não há necessidade validada de banco de dados ou autenticação para o motor de cálculo atual.

## Funcionalidades disponíveis no código local

- Saldo de salário.
- Décimo terceiro proporcional.
- Férias proporcionais, adquiridas e vencidas, com os adicionais correspondentes.
- Aviso prévio proporcional, trabalhado, indenizado e não cumprido, conforme a modalidade.
- Desconto de aviso não cumprido no pedido de demissão.
- Depósito rescisório e multa do FGTS.
- INSS e IRRF, calculados separadamente para verbas mensais e décimo terceiro.
- Total bruto e total líquido.
- Validação de combinações entre modalidade de desligamento e situação do aviso.
- API de cálculo e endpoint de saúde.

### Modalidades

| Modalidade | Identificador da API |
| --- | --- |
| Dispensa sem justa causa | `dismissal_without_cause` |
| Pedido de demissão | `resignation` |
| Acordo entre empregado e empregador | `mutual_agreement` |
| Dispensa com justa causa | `dismissal_with_cause` |

## Organização

```text
backend/
  app/
    main.py
    api/          # Endpoints HTTP
    domain/       # Regras e cálculos isolados
    schemas/      # Entradas e respostas validadas
    services/     # Orquestração do cálculo
  tests/          # Testes de domínio, serviço, schemas e API
frontend/         # Estrutura inicial da interface
```

As regras financeiras ficam no domínio. O serviço coordena os cálculos, os schemas definem o contrato e os endpoints expõem as operações HTTP.

## Execução local do backend

Pré-requisitos: Git e Python 3.14 disponível no sistema. Os comandos abaixo usam PowerShell e partem da raiz do repositório.

```powershell
cd backend
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi "pydantic>=2,<3" "uvicorn[standard]" pytest httpx
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Se já existir um ambiente virtual copiado de outra máquina, ele deve ser recriado antes da execução. O projeto ainda não possui manifesto de dependências do backend versionado; a instalação acima é provisória e não fixa versões reproduzíveis. Criar e validar esse manifesto é uma prioridade do roteiro.

Com a API iniciada:

- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- OpenAPI: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json).
- Saúde: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

### Testes

Execute dentro de `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

A suíte cobre regras de domínio, schemas, serviço e chamadas HTTP. Ainda está prevista a ampliação da cobertura HTTP dos cenários mais recentes de aviso prévio e dos casos extremos.

## API

### Saúde

`GET /health`

```json
{"status": "ok"}
```

### Cálculo

`POST /api/v1/terminations/calculate`

Exemplo de corpo de requisição:

```json
{
  "monthly_salary": "3000.00",
  "admission_date": "2024-01-10",
  "termination_date": "2026-08-20",
  "termination_type": "dismissal_without_cause",
  "notice_period_type": "indemnified",
  "acquired_vacation_periods": 0,
  "overdue_vacation_periods": 0,
  "fgts_rescission_base": "12000.00"
}
```

`monthly_salary` deve ser positivo. Os períodos de férias e a base do FGTS não podem ser negativos e têm zero como padrão. Datas usam o formato `AAAA-MM-DD`.

`notice_period_type` aceita `worked`, `indemnified` e `not_worked`, conforme a modalidade. O campo é opcional para preservar o comportamento anterior do motor. No modelo atual, a justa causa não admite uma situação explícita de aviso e deve usar o campo omitido ou `null`.

A resposta contém os valores das verbas, os dias e a projeção do aviso, depósitos e multa do FGTS, INSS, IRRF e os totais. Os campos monetários usam `Decimal` e são serializados como strings pelo schema atual.

| Grupo | Campos principais |
| --- | --- |
| Salário e décimo terceiro | `salary_balance`, `thirteenth_salary` |
| Férias | `proportional_vacation`, `acquired_vacation`, `overdue_vacation` e respectivos campos de adicional |
| Aviso | `notice_period_days`, `notice_period_value`, `notice_period_discount`, `projected_termination_date` |
| FGTS | `fgts_termination_deposit`, `fgts_penalty` |
| Tributos | `inss_monthly`, `inss_thirteenth`, `inss_total`, `irrf_monthly`, `irrf_thirteenth`, `irrf_total` |
| Totais | `total`, `net_total` |

Erros de domínio tratados como `ValueError` retornam HTTP 400. Erros de validação de entrada e funcionalidades não suportadas retornam HTTP 422. O Swagger permite consultar o contrato completo e executar requisições.

## Decisões e limites atuais

- `total` representa o valor bruto das verbas pagas diretamente ao trabalhador.
- `net_total = total - inss_total - irrf_total - notice_period_discount`.
- Depósitos e multa do FGTS ficam separados dos totais de pagamento direto.
- `fgts_rescission_base` é a base informada para a multa; não representa necessariamente saldo disponível para saque.
- O motor não reconstrói o histórico de depósitos do FGTS.
- As tabelas tributárias implementadas são específicas de 2026; não há suporte automático a outros anos.
- Dependentes, pensão alimentícia e previdência complementar ainda não são integralmente contemplados.
- Saque do FGTS e informações de seguro-desemprego ainda não estão implementados.
- Aviso parcialmente cumprido, dispensa do cumprimento e a interpretação das datas no aviso trabalhado precisam de revisão de escopo.
- A projeção do aviso no acordo mantém a decisão existente até uma revisão fundamentada e aprovada.
- Arredondamentos e premissas financeiras ainda terão documentação e auditoria próprias.

Os resultados são estimativas dentro do escopo implementado. O projeto ainda não foi declarado validado para uso público como cálculo trabalhista ou fiscal definitivo.

## Roteiro de desenvolvimento

Cada etapa será apresentada para revisão antes de sua implementação. A proposta deve explicar escopo, arquivos envolvidos, critérios de aceite e validação. A continuidade depende da decisão do responsável pelo projeto.

| Etapa | Entrega prevista | Critério de aceite |
| --- | --- | --- |
| 1. Base reproduzível | Recuperar o ambiente Python, definir dependências e revisar as alterações locais antes de consolidá-las no Git | Instalação documentada e suíte executada com resultado registrado |
| 2. Direitos associados à rescisão | Definir a modelagem informativa de FGTS e seguro-desemprego com fontes oficiais | Modelagem aprovada, domínio testado e integração validada no serviço e na API |
| 3. Validações e regressões | Auditar lacunas de entrada, datas, férias e situações não suportadas | Casos negativos e extremos relevantes cobertos, sem regressões |
| 4. Auditoria das regras | Revisar aviso, décimo terceiro, férias, FGTS e tributos | Premissas e fontes registradas; divergências avaliadas antes de mudanças |
| 5. Fechamento do backend V1 | Estabilizar contrato, exemplos OpenAPI, erros e documentação | Testes aprovados, API verificada e limitações explícitas |
| 6. Interface | Revisar a stack existente e construir formulário e apresentação dos resultados | Fluxo responsivo, acessível e integrado à API |
| 7. Qualidade e publicação | Definir verificações automatizadas e infraestrutura, validar o fluxo completo e publicar | Aplicação acessível, verificações aprovadas e instruções de manutenção |
| 8. Apresentação no portfólio | Adicionar demonstração, capturas e resumo das decisões técnicas | Repositório compreensível e aplicação demonstrável para recrutadores |

A modelagem dos direitos deverá distinguir possibilidade de solicitação de concessão efetiva e considerar restrições individuais. Nenhum valor de saque será calculado a partir de uma base inadequada. O arquivo `termination_benefits.py` só será criado após a revisão da proposta.

Mudanças de arquitetura, novas dependências, alterações de regras consolidadas e infraestrutura serão justificadas antes da execução. A evolução será incremental, com testes relevantes a cada funcionalidade.

## Objetivo da V1

Entregar uma aplicação completa, testada, documentada e publicada, com cálculos transparentes dentro de um escopo explícito e decisões técnicas que possam ser discutidas em uma avaliação profissional.
