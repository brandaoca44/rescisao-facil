# Premissas e validações do cálculo

## Saldo salarial

A V1 mantém a convenção de salário mensal dividido por 30. O intervalo considera a admissão quando ela ocorre no mês do desligamento e inclui o último dia trabalhado. Um mês civil completo corresponde a 30 dias remunerados, inclusive em fevereiro; períodos parciais ficam limitados a 30 dias.

Exemplos com salário de R$ 3.000: admissão em 15/08 e saída em 20/08 resultam em seis dias e R$ 600; um mês completo resulta em R$ 3.000. A saída no dia 31 não é rejeitada.

Essa é uma convenção explícita da V1, preservada em relação ao divisor existente, e não uma afirmação de aplicação universal a todas as categorias ou convenções coletivas. O [Ministério do Trabalho](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/proteja/duvidas-frequentes) descreve o saldo como pagamento dos dias trabalhados no mês. O [manual do eSocial para MEI](https://www.gov.br/esocial/pt-br/microempreendedor-individual/manual-web-mei) utiliza dias do mês civil em seu próprio contexto; esse método não foi generalizado automaticamente para o projeto.

## Datas e anos bissextos

A data de desligamento não pode anteceder a admissão. O dia de admissão e o último dia trabalhado entram na contagem do intervalo.

No aniversário anual de uma admissão em 29/02, o marco usado em anos não bissextos é 01/03. A [Lei 810/1949, art. 3º](https://www.planalto.gov.br/ccivil_03/leis/1930-1949/l810-49.htm) estabelece o primeiro dia subsequente quando o dia correspondente não existe. Os períodos anuais de férias permanecem ancorados na admissão original, evitando perder o dia 29 quando um novo ano bissexto é alcançado.

## Férias informadas

Os campos de férias adquiridas e vencidas representam períodos distintos ainda não quitados. Sua soma não pode superar os períodos aquisitivos completos no vínculo. A quantidade informada como vencida também não pode superar os períodos cujo prazo concessivo já terminou.

A verificação usa a data projetada do aviso quando essa projeção existe no modelo. A inclusão do último dia pode completar um período aquisitivo; nesse caso, o mesmo período não é novamente pago como férias proporcionais.

A validação estabelece limites possíveis e não reconstrói férias já gozadas, afastamentos ou todo o histórico do contrato. As quantidades continuam sendo informadas pelo usuário. A referência é a [CLT, arts. 130, 134, 137 e 146](https://www2.camara.leg.br/legin/fed/declei/1940-1949/decreto-lei-5452-1-maio-1943-415500-normaatualizada-pe.html).

## Valores financeiros e erros

Salário e base rescisória do FGTS aceitam até dez dígitos inteiros e duas casas decimais, com valor máximo de R$ 9.999.999.999,99. Trata-se de limite técnico da API, não de limite legal. Salário deve ser positivo; a base do FGTS pode ser zero. Valores não finitos, negativos ou com precisão superior à suportada são rejeitados na entrada, com HTTP 422.

Os cálculos usam Decimal. O fator financeiro do aviso adota arredondamento explícito ROUND_HALF_UP para centavos. Erros de domínio, como férias incompatíveis ou combinação inválida de aviso, retornam HTTP 400. Anos tributários não suportados retornam HTTP 422 antes das operações de projeção de datas.

Depósitos e multa do FGTS permanecem fora dos totais de pagamento direto. O valor líquido continua sendo o bruto menos INSS, IRRF e desconto de aviso. No acordo, o valor indenizado é reduzido à metade e a projeção mantém o prazo integral do aviso proporcional adotado pelo motor. As tabelas tributárias implementadas correspondem a 2026; sua auditoria completa e as particularidades individuais permanecem fora do escopo destas validações.
