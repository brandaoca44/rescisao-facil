# Frontend do Rescisão Fácil

O formulário envia os dados para a rota interna do Next.js. Essa rota encaminha a requisição ao FastAPI e retorna a estimativa, incluindo os descontos, o FGTS e as condições dos benefícios.

## Configuração local

Em `.env.local`, defina `BACKEND_API_URL` com a origem do FastAPI. Use o endereço e a porta confirmados para esta execução. O Next.js lê essa variável no servidor.

Com as portas confirmadas e o backend em execução, inicie o frontend com `npm run dev -- --port PORTA`, substituindo `PORTA` pela porta escolhida. Para conferir a compilação, execute `npm run lint` e `npm run build` dentro de `frontend`.
