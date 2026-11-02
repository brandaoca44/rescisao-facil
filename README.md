# Rescisão Fácil

Aplicação web para estimar os valores de uma rescisão trabalhista brasileira e ajudar o trabalhador a compreender as verbas e os descontos envolvidos no encerramento de um contrato de trabalho.

A partir do salário, das datas do vínculo, da modalidade de desligamento e das informações de férias e FGTS, o sistema calcula as parcelas da rescisão e apresenta o total bruto, os descontos e o total líquido.

## Funcionalidades

- Cálculo do saldo de salário.
- Décimo terceiro proporcional, com detalhamento por ano e compensação de pagamentos e retenções anteriores informados.
- Férias proporcionais, adquiridas e vencidas, com adicional de um terço.
- Aviso prévio proporcional, considerando aviso trabalhado, indenizado ou não cumprido conforme a modalidade.
- Desconto do aviso não cumprido no pedido de demissão.
- Depósito rescisório e multa do FGTS.
- Cálculo de INSS e IRRF sobre as verbas contempladas pelo sistema.
- Detalhamento das verbas, dos descontos e dos totais bruto e líquido.
- Informações por modalidade sobre saque do FGTS e possibilidade de solicitar seguro-desemprego, com as condições aplicáveis.

Os valores de FGTS e da multa rescisória são apresentados separadamente das verbas pagas diretamente ao trabalhador.

## Modalidades de rescisão

- Dispensa sem justa causa.
- Pedido de demissão.
- Acordo entre empregado e empregador.
- Dispensa com justa causa.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Backend | Python, FastAPI e Pydantic |
| Cálculos financeiros | Decimal |
| Testes automatizados | pytest e TestClient |
| Servidor da API | Uvicorn |
| Estrutura inicial do frontend | Next.js, React, TypeScript e Tailwind CSS |

## Arquitetura

O backend separa as regras de cálculo, a validação de dados e a comunicação HTTP:

- **Domínio:** regras de negócio e cálculos financeiros.
- **Schemas:** validação das entradas e definição das respostas.
- **Serviços:** coordenação das etapas do cálculo.
- **API:** disponibilização dos resultados por endpoints HTTP.
- **Testes:** verificação das regras e do comportamento da API.

## API

O endpoint `POST /api/v1/terminations/calculate` recebe os dados do contrato e retorna o detalhamento da rescisão.

A documentação interativa é disponibilizada pelo FastAPI em `/docs`, com os campos de entrada, os formatos de resposta e a possibilidade de testar requisições.

## Desenvolvimento

O motor de cálculo possui um checkpoint técnico documentado e validado. A interface e sua integração com a API são as próximas etapas de desenvolvimento.

As próximas entregas incluem revisão das regras, ampliação das validações, conclusão da interface e publicação da aplicação.

## Escopo dos cálculos

Os resultados são estimativas para as situações contempladas pelo sistema. As tabelas de INSS e IRRF implementadas correspondem a 2026. Particularidades como dependentes, pensão alimentícia e previdência complementar ainda não são integralmente contempladas.

## Documentação

- [Execução do backend e uso da API](backend/README.md).
- [Premissas e validações dos cálculos](docs/calculation-rules.md).
- [Regras tributárias de 2026](docs/tax-rules.md).
- [Contagem e validação das férias](docs/vacation-rules.md).
- [Escopo e critérios de aceite do backend V1](docs/backend-v1-acceptance.md).
