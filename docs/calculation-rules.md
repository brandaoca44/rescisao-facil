# Premissas e validações do cálculo

## Saldo salarial

A V1 mantém a convenção de salário mensal dividido por 30. O intervalo considera a admissão quando ela ocorre no mês do desligamento e inclui o último dia trabalhado. Um mês civil completo corresponde a 30 dias remunerados, inclusive em fevereiro; períodos parciais ficam limitados a 30 dias.

Exemplos com salário de R$ 3.000: admissão em 15/08 e saída em 20/08 resultam em seis dias e R$ 600; um mês completo resulta em R$ 3.000. A saída no dia 31 não é rejeitada.

Essa é uma convenção explícita da V1, preservada em relação ao divisor existente, e não uma afirmação de aplicação universal a todas as categorias ou convenções coletivas. O [Ministério do Trabalho](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/proteja/duvidas-frequentes) descreve o saldo como pagamento dos dias trabalhados no mês. O [manual do eSocial para MEI](https://www.gov.br/esocial/pt-br/microempreendedor-individual/manual-web-mei) utiliza dias do mês civil em seu próprio contexto; esse método não foi generalizado automaticamente para o projeto.

## Datas e anos bissextos

A data de desligamento não pode anteceder a admissão. O dia de admissão e o último dia trabalhado entram na contagem do intervalo.

No aniversário anual de uma admissão em 29/02, o marco usado em anos não bissextos é 01/03. A [Lei 810/1949, art. 3º](https://www.planalto.gov.br/ccivil_03/leis/1930-1949/l810-49.htm) estabelece o primeiro dia subsequente quando o dia correspondente não existe. Os períodos anuais de férias permanecem ancorados na admissão original, evitando perder o dia 29 quando um novo ano bissexto é alcançado.

## Décimo terceiro e projeção entre anos

A contagem começa no ano do desligamento, sem recuperar débitos de anos anteriores, e segue até o fim da projeção. Cada ano é apurado separadamente, contando apenas meses com ao menos 15 dias de vínculo, inclusive os alcançados pela projeção do aviso. O valor de cada ano é arredondado para centavos antes da soma.

`thirteenth_salary_by_year` informa ano, avos e valor. `thirteenth_salary` é a soma dessas parcelas e pode superar um salário mensal quando há avos de dois anos. Anos com zero avos aparecem com valor zero; modalidades sem décimo terceiro retornam uma lista vazia.

O total corrigido alimenta as bases já existentes de FGTS, INSS e IRRF. A V1 mantém o cenário de quitação única na rescisão de 2026: o detalhamento anual não cria novas datas de pagamento, novas competências tributárias ou tabelas de 2027. Pagamentos anteriores e retenções devem ser informados em `thirteenth_previous_payment`; valores omitidos são considerados zero.

Referências: [Lei 4.090/1962, art. 1º](https://legis.senado.gov.br/norma/545928/publicacao/34620254), [CLT, art. 487, § 1º](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452compilado.htm), [IN RFB 1.500/2014, art. 13 — quitação do décimo terceiro](https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=57670&visao=anotado) e [IN RFB 2.110/2022, arts. 66 a 70](https://normas.receita.fazenda.gov.br/sijut2consulta/consulta/link.action?idAto=126687&visao=original).

## Compensação do décimo terceiro anterior

`thirteenth_previous_payment` representa pagamentos brutos, retenções do empregado e FGTS depositado exclusivamente sobre o décimo terceiro do ano do desligamento. A projeção do ano futuro não aumenta o limite de histórico aceito para o ano atual.

O bruto integral e seus avos não mudam com o histórico. Os tributos são apurados sobre esse bruto e só depois são abatidas as retenções anteriores. O histórico reduz o valor a reter, não a base tributável; a dedução de INSS na apuração do IRRF continua sendo a contribuição integral correspondente ao décimo terceiro.

O saldo bruto é o décimo terceiro integral menos o bruto pago. O valor líquido da rescisão desconta esse bruto pago e somente os tributos adicionais. O FGTS anterior reduz o depósito rescisório informado, sem alterar a base externa da multa. Exemplo: direito total de R$ 3.250 e R$ 3.000 brutos pagos, com R$ 248,60 de INSS já retido, resultam em R$ 250 de saldo bruto e R$ 30 de INSS adicional no cenário documentado da virada do ano.

Os valores devem ser não negativos, finitos e ter até duas casas decimais. Retenções anteriores somadas não podem exceder o bruto pago. O histórico bruto não pode superar o direito do ano atual. Retenções acima dos tributos recalculados, FGTS acima do depósito devido e FGTS informado sem pagamento bruto são rejeitados. Essas são fronteiras do escopo suportado; não significam que situações reais de restituição ou recuperação de adiantamento sejam proibidas pela legislação.

Adiantamentos excedentes e devoluções exigem evolução própria, inclusive limites de compensação e procedimentos de restituição. A V1 retorna erro explícito nesses casos em vez de presumir recuperação ou devolução automática.

Referências: [Lei 4.749/1965, art. 3º](https://www.planalto.gov.br/ccivil_03/leis/l4749.htm), [IN RFB 1.500/2014, art. 13, § 3º](https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=57670&visao=anotado), [IN RFB 2.110/2022, art. 66](https://normas.receita.fazenda.gov.br/sijut2consulta/consulta/link.action?idAto=126687&visao=original) e [MTE — FGTS e adiantamentos do décimo terceiro, pergunta 02.14](https://www.gov.br/trabalho-e-emprego/pt-br/servicos/empregador/fgtsdigital/perguntas-frequentes).

## Férias informadas

Os campos de férias adquiridas e vencidas representam períodos distintos ainda não quitados. Sua soma não pode superar os períodos aquisitivos completos no vínculo. A quantidade informada como vencida também não pode superar os períodos cujo prazo concessivo já terminou. As férias simples são limitadas aos períodos ainda dentro do prazo concessivo, sem reclassificar automaticamente o histórico informado.

A verificação usa a data projetada do aviso quando essa projeção existe no modelo. A inclusão do último dia pode completar um período aquisitivo; nesse caso, o mesmo período não é novamente pago como férias proporcionais.

A validação estabelece limites possíveis e não reconstrói férias já gozadas, afastamentos ou todo o histórico do contrato. As quantidades continuam sendo informadas pelo usuário. A contagem mensal permanece ancorada no início do período, sem herdar deslocamentos de fevereiro. Os casos de fronteira e as limitações estão nas [regras de férias](vacation-rules.md). A referência é a [CLT, arts. 130, 134, 137 e 146](https://www2.camara.leg.br/legin/fed/declei/1940-1949/decreto-lei-5452-1-maio-1943-415500-normaatualizada-pe.html).

## Valores financeiros e erros

Salário e base rescisória do FGTS aceitam até dez dígitos inteiros e duas casas decimais, com valor máximo de R$ 9.999.999.999,99. Trata-se de limite técnico da API, não de limite legal. Salário deve ser positivo; a base do FGTS pode ser zero. Valores não finitos, negativos ou com precisão superior à suportada são rejeitados na entrada, com HTTP 422.

Os cálculos usam Decimal. O fator financeiro do aviso adota arredondamento explícito ROUND_HALF_UP para centavos. Erros de domínio, como férias incompatíveis ou combinação inválida de aviso, retornam HTTP 400. Anos tributários não suportados retornam HTTP 422 antes das operações de projeção de datas.

Depósitos e multa do FGTS permanecem fora dos totais de pagamento direto. O valor líquido é o bruto menos as retenções adicionais de INSS e IRRF, o desconto de aviso e o décimo terceiro bruto já pago informado. No acordo, o valor indenizado é reduzido à metade e a projeção mantém o prazo integral do aviso proporcional adotado pelo motor. As tabelas tributárias implementadas correspondem a 2026; a revisão do escopo suportado e suas limitações estão em [regras tributárias](tax-rules.md).

## Direitos associados à modalidade

O objeto `benefits` informa regras gerais decorrentes do desligamento:

| Modalidade | Fração de saque na sistemática saque-rescisão | Seguro-desemprego possível pela modalidade |
| --- | --- | --- |
| Sem justa causa | 1.00 | Sim, condicionado aos demais requisitos |
| Pedido de demissão | 0.00 | Não |
| Acordo | 0.80 | Não |
| Justa causa | 0.00 | Não |

A fração zero indica que o desligamento não libera o saldo por esse motivo; outras hipóteses de saque não são avaliadas. Os percentuais não se aplicam automaticamente a quem está no saque-aniversário. Nessa sistemática, a regra geral do desligamento sem justa causa ou por acordo preserva o saque da multa rescisória, sem liberar o restante do saldo por esse motivo. Eventuais regras extraordinárias e bloqueios exigem análise específica.

A possibilidade de solicitar seguro-desemprego não confirma concessão. O projeto não conhece todo o histórico salarial, as solicitações anteriores, a renda e os demais requisitos individuais. Por isso, o indicador permanece condicionado mesmo para contratos curtos.

As informações são independentes da base da multa do FGTS e não entram no cálculo do bruto ou do líquido. Não é calculado valor de saque nem valor ou quantidade de parcelas do seguro-desemprego.

Referências oficiais consultadas em 02/11/2026:

- [CAIXA — sistemáticas de saque do FGTS](https://www.caixa.gov.br/beneficios-trabalhador/fgts/saque-FGTS/Paginas/default.aspx).
- [FGTS — rescisão por acordo e restrição do saque-aniversário](https://www.fgts.gov.br/Paginas/subpaginas/saque-rescisao-contrato-de-trabalho-por-acordo.aspx).
- [CLT, artigo 484-A](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452compilado.htm).
- [MTE — modalidades de desligamento](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/proteja/duvidas-frequentes).
- [Governo Federal — requisitos do seguro-desemprego](https://www.gov.br/pt-br/temas/perguntas-frequentes-seguro-desemprego).
