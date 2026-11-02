# Proposta do frontend V1

Status: proposta para revisão; a implementação funcional da interface ainda não foi iniciada. O backend possui [checkpoint técnico validado](backend-v1-acceptance.md).

## Objetivo e tecnologias

Permitir que um trabalhador informe os dados do vínculo, obtenha uma estimativa e compreenda as verbas, os descontos e as condições dos direitos informados.

A proposta mantém Next.js, React, TypeScript e Tailwind CSS já presentes em `frontend/`. A etapa inicial não exige novas bibliotecas, autenticação, persistência ou banco de dados. O layout será responsivo, em português do Brasil, com tipografia legível, fundo claro e uma identidade visual sóbria.

## Jornada principal

1. Ler uma apresentação curta do cálculo e do escopo suportado.
2. Informar os dados do vínculo e a situação do aviso.
3. Preencher as verbas e o histórico aplicáveis ao caso.
4. Solicitar o cálculo e receber indicação de carregamento ou correções necessárias.
5. Consultar o resultado, revisar as premissas e ajustar os dados quando necessário.

A proposta usa uma única página com seções claras, evitando um formulário extenso sem agrupamento. O resumo do resultado aparece após o cálculo; os detalhes podem ser expandidos.

## Formulário

| Seção | Conteúdo |
| --- | --- |
| Vínculo | Salário mensal bruto, admissão, desligamento efetivo e modalidade |
| Aviso | Apenas as situações compatíveis com a modalidade; na justa causa o campo é omitido |
| Férias pendentes | Períodos integrais simples e vencidos, com orientação para considerar a data projetada |
| FGTS | Base da multa, identificada separadamente do saldo disponível para saque |
| Décimo terceiro anterior | Seção opcional para bruto já pago, INSS, IRRF e FGTS anteriores |

A situação do aviso será enviada explicitamente nas modalidades aplicáveis. O formulário explicará que aviso trabalhado usa a data final do cumprimento e que a opção de aviso não cumprido no pedido de demissão representa o cenário com desconto. Dispensa de cumprimento e aviso parcial não serão apresentados como casos suportados.

Datas fora do ano tributário suportado e valores incompatíveis terão orientação clara. O formulário distinguirá ausência de informação de uma declaração de valor zero, especialmente nas férias e nos pagamentos anteriores. As quantidades integrais de férias continuarão sendo informadas pelo usuário; a interface deverá destacar a necessidade de revisão conforme a projeção calculada.

## Resultados

- Destaque para o líquido estimado e o bruto integral antes dos abatimentos.
- Detalhamento de saldo salarial, aviso, décimo terceiro por ano, férias e adicionais.
- Descontos separados: INSS, IRRF, aviso não cumprido e décimo terceiro bruto já pago.
- Histórico e saldo do décimo terceiro, permitindo conferir o que foi compensado.
- FGTS e multa em bloco próprio, com identificação de que não integram o pagamento direto.
- Direitos informativos acompanhados das condições de saque e concessão.
- Data projetada do aviso e premissas relevantes para revisar o cálculo.

Um líquido negativo será apresentado com explicação, sem caracterizá-lo como dívida automaticamente exigível. As limitações do [backend V1](backend-v1-acceptance.md) devem ficar acessíveis antes do envio e junto ao resultado.

## Integração proposta

A interface consumirá o contrato existente, mantendo os cálculos no backend. Valores monetários serão tratados e enviados como strings decimais, com apresentação em reais; a formatação não poderá alterar o valor utilizado na requisição.

Propõe-se uma rota interna do Next.js para encaminhar a requisição ao FastAPI. A URL do backend será configurada no servidor, evitando depender de uma porta fixa no navegador. A integração tratará timeout, indisponibilidade e os dois formatos de erro 422, além dos erros de domínio 400.

A organização prevista separa formulário, resultados, tipos do contrato e cliente da API. As validações locais orientarão o preenchimento; o backend continuará sendo a autoridade para validar e calcular.

## Entregas incrementais

| Etapa | Entrega | Validação |
| --- | --- | --- |
| 1. Interface inicial | Identidade visual, apresentação, formulário responsivo e campos condicionais | Lint, build, revisão de rótulos e navegação por teclado |
| 2. Integração | Envio ao FastAPI, resultados reais e estados de carregamento e erro | Exemplos das quatro modalidades e cenários de erro |
| 3. Refinamento | Detalhamento, condições dos benefícios e experiência em telas pequenas | Revisão funcional, acessibilidade e aprovação do fluxo completo |

Cada etapa será apresentada para revisão antes da próxima implementação. Ferramentas adicionais de teste, se necessárias, serão propostas antes da instalação.

## Serviços e portas

Nenhum servidor ou serviço é iniciado durante a definição da proposta. Antes de executar a interface ou a integração local, verificar as portas utilizadas e confirmar a escolha com o responsável. A proposta não exige Docker ou PostgreSQL. As URLs e portas de desenvolvimento serão definidas depois dessa confirmação.
