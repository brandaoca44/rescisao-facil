# Férias — contagem e validação

## Contagem dos avos

As férias proporcionais usam o período aquisitivo vigente, com um avo por mês de serviço e acréscimo de um avo quando a fração restante tem ao menos 15 dias. O dia de admissão e o último dia do vínculo entram na contagem. Um período aquisitivo completo é tratado como férias adquiridas, sem ser novamente pago como proporcional.

Os marcos mensais são calculados a partir do início do período, preservando a referência original. Quando o dia correspondente não existe, o marco é o primeiro dia subsequente. A passagem por fevereiro não altera permanentemente o dia usado nos meses seguintes.

Exemplos para admissão em 31/01/2026:

| Referência | Avos proporcionais |
| --- | --- |
| 14/03/2026 | 1 |
| 15/03/2026 | 2 |
| 13/04/2026 | 2 |
| 14/04/2026 | 3 |

O primeiro marco mensal é 01/03 e o segundo é 31/03. Para uma admissão em 29/02, os marcos anuais em anos não bissextos usam 01/03, mantendo a admissão original como referência quando um novo ano bissexto é alcançado.

## Períodos simples e vencidos

`acquired_vacation_periods` e `overdue_vacation_periods` representam períodos integrais distintos, não quitados, na data projetada do desligamento. O primeiro campo informa férias adquiridas ainda dentro do prazo concessivo; o segundo informa períodos com prazo concessivo encerrado, pagos em dobro. O mesmo período não pode aparecer nos dois campos.

O motor verifica três limites: a soma não supera os períodos aquisitivos completos; a quantidade de férias vencidas não supera os períodos com prazo concessivo encerrado; e a quantidade simples não supera os períodos ainda dentro desse prazo. São limites possíveis, não uma reconstrução de férias efetivamente gozadas.

A conclusão do período aquisitivo inclui seu último dia. O prazo concessivo só é considerado encerrado após seu último dia. Exemplo com admissão em 10/01/2024: o segundo período aquisitivo termina em 09/01/2026 e o prazo concessivo do primeiro encerra-se após essa data; o primeiro período passa a ser classificado como vencido em 10/01/2026. Na fronteira de 09/01, dois períodos completos ainda cabem na classificação simples; no dia seguinte, o primeiro pertence à classificação vencida.

## Projeção e valores

Quando o modelo aplica projeção do aviso, essa data é usada na contagem e na validação. Os campos de períodos devem incluir os adquiridos pela projeção e refletir os prazos concessivos nessa mesma data. Sem projeção, usa-se a data de desligamento. O aviso não cumprido no pedido de demissão não cria uma projeção.

O motor não acrescenta automaticamente períodos integrais às quantidades informadas. Informar zero significa declarar ausência de períodos integrais pendentes, inclusive os que seriam completados pela projeção. É necessário revisar essas quantidades ao fornecer os dados. Essa convenção preserva o contrato da API e evita duplicar períodos que o usuário já incluiu.

Cada período simples corresponde a um salário, mais um terço. Cada período integral vencido corresponde a dois salários, mais um terço sobre esse valor dobrado. Férias indenizadas ficam fora das bases tributárias implementadas. O pagamento simples ou em dobro de períodos adquiridos é preservado na justa causa; as férias proporcionais seguem a regra já adotada pelo projeto para essa modalidade.

## Limitações

A V1 considera períodos integrais pendentes informados pelo usuário. Não reconstrói fracionamentos, férias parcialmente gozadas, valores já pagos, faltas, afastamentos ou mudanças de período aquisitivo. Não calcula dobra parcial de dias gozados após o prazo concessivo. Casos de perda ou reinício do período aquisitivo exigem modelagem específica.

## Fontes oficiais

- [CLT, arts. 130, 134, 137 e 146](https://www2.camara.leg.br/legin/fed/declei/1940-1949/decreto-lei-5452-1-maio-1943-415500-normaatualizada-pe.html).
- [Lei 810/1949 — marcos de mês e ano](https://planalto.gov.br/ccivil_03/leis/1930-1949/l810-49.htm).
- [MTE — períodos aquisitivo e concessivo, férias proporcionais e dobra](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/proteja/duvidas-frequentes).
- [TRT da 9ª Região — dobra apenas dos dias excedentes no gozo parcial](https://www.trt9.jus.br/portal/noticias.xhtml?id=6963102).
