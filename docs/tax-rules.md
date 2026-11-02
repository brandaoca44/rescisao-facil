# INSS e IRRF — escopo de 2026

## Resultado da revisão

As faixas, alíquotas e limites implementados coincidem com as tabelas oficiais consultadas em 02/11/2026. A revisão confirmou a separação das bases mensal e de décimo terceiro e a aplicação do desconto simplificado e da redução de 2026 ao décimo terceiro.

Foi corrigida a dispensa de retenção mensal de IRRF apurado em valor igual ou inferior a R$ 10,00. Essa dispensa não é aplicada ao décimo terceiro, tributado exclusivamente na fonte. A correção altera apenas o líquido nos cenários atingidos, sem alterar as verbas brutas.

## INSS

| Parcela da base de contribuição | Alíquota |
| --- | --- |
| Até R$ 1.621,00 | 7,5% |
| De R$ 1.621,00 até R$ 2.902,84, sobre o excedente | 9% |
| De R$ 2.902,84 até R$ 4.354,27, sobre o excedente | 12% |
| De R$ 4.354,27 até R$ 8.475,55, sobre o excedente | 14% |

O cálculo soma as parcelas progressivas, limita a base ao teto e arredonda o resultado para centavos com ROUND_HALF_UP. As bases mensal e de décimo terceiro são calculadas separadamente, cada uma com seu teto. Nesta V1, correspondem ao saldo salarial e ao décimo terceiro proporcional, respectivamente.

## IRRF

A base é o rendimento tributável menos a maior dedução entre o INSS correspondente e o desconto simplificado de R$ 607,20. As deduções individuais ainda não contempladas pelo projeto não são simuladas.

Após aplicar a tabela progressiva mensal, o motor aplica a redução de 2026 usando o rendimento tributável antes das deduções: até R$ 5.000 o imposto é zerado; até R$ 7.350 a redução é de R$ 978,62 menos 0,133145 vezes o rendimento; acima desse limite não há redução. A redução é limitada ao imposto calculado.

A apuração do imposto ocorre em `calculate_irrf`. A retenção mensal, em `calculate_monthly_irrf`, aplica adicionalmente a dispensa até R$ 10. O cálculo do décimo terceiro usa a primeira função, mantendo a tributação exclusiva sem essa dispensa. Os valores do imposto progressivo e da redução são arredondados para centavos com ROUND_HALF_UP antes da subtração.

Exemplos com a contribuição previdenciária de 2026 calculada pelo próprio motor:

| Rendimento | INSS | Imposto antes da dispensa mensal | Retenção mensal |
| --- | --- | --- | --- |
| R$ 5.027,89 | R$ 505,42 | R$ 9,99 | R$ 0,00 |
| R$ 5.027,94 | R$ 505,43 | R$ 10,01 | R$ 10,01 |
| R$ 6.000,00 | R$ 641,51 | R$ 385,10 | R$ 385,10 |

Os exemplos didáticos de IRRF publicados pela Receita informam suas próprias deduções previdenciárias. Os testes usam essas deduções para reproduzir os exemplos, sem substituir por elas a tabela de INSS de 2026 do projeto.

## Incidências e limitações

Aviso indenizado, férias indenizadas e respectivos adicionais, FGTS e multa não entram nas bases tributárias implementadas. O décimo terceiro permanece remuneratório, inclusive seus reflexos da projeção do aviso, e é apurado separadamente.

A V1 estima um pagamento isolado e não soma outros pagamentos tributáveis da mesma fonte no mês, nem desconta imposto mensal já retido. O histórico específico do décimo terceiro pode ser informado em `thirteenth_previous_payment`. Assim, a dispensa mensal pressupõe que não existam outros pagamentos relevantes a agregar. Também não considera vínculos concomitantes para INSS, dependentes, pensão alimentícia ou previdência complementar.

O ano das tabelas é determinado pela data de desligamento informada, sob a premissa de quitação única na rescisão. A projeção em outro ano é detalhada em `thirteenth_salary_by_year`; a soma das parcelas alimenta a apuração existente sobre o décimo terceiro da rescisão. A separação dos avos não introduz datas de pagamento ou tabelas tributárias futuras. Adiantamentos e retenções anteriores do décimo terceiro do ano do desligamento são compensados quando informados, sem reduzir a base integral do imposto. O projeto não modela quitação em outra data, diferenças de competência, recuperação de adiantamentos excedentes, restituições ou regras de rendimentos recebidos acumuladamente de anos anteriores. Esses cenários exigem evolução específica antes de uso como folha definitiva.

## Fontes oficiais

- [INSS — tabela de contribuição de 2026 e bases separadas](https://www.gov.br/inss/pt-br/direitos-e-deveres/inscricao-e-contribuicao/tabela-de-contribuicao-mensal).
- [Receita Federal — tributação de 2026](https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas/2026).
- [Receita Federal — exemplos de aplicação da redução](https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/tabelas/exemplos-de-aplicacao-da-lei-15-270-2025).
- [eSocial — desconto simplificado nos cálculos mensal e de décimo terceiro](https://www.gov.br/esocial/pt-br/empresas/perguntas-frequentes/perguntas-frequentes-producao-empresas-e-ambiente-de-testes).
- [Receita Federal — redução também aplicável ao décimo terceiro](https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2025/dezembro/receita-federal-orienta-fontes-pagadoras-e-contribuintes-a-calcular-a-reducao-do-imposto-de-renda-a-partir-de-1o-de-janeiro-de-2026).
- [Receita Federal — dispensa de retenção e art. 67 da Lei 9.430/1996](https://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=45564).
- [Receita Federal — verbas isentas na rescisão](https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/malha-fiscal/antecipacao/rendimentos-recebidos-de-empresa/fui-demitido).
- [PGFN — aviso indenizado e natureza remuneratória de seus reflexos no décimo terceiro](https://www.gov.br/pgfn/pt-br/assuntos/representacao-judicial/lista-dispensa-contestar-recorrer/lista-de-dispensa-de-contestar-e-recorrer-art-2o-v-vii-e-a7a7-3o-a-8o-da-portaria-pgfn-no-502-2016).
