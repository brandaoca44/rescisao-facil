const headers = { "Cache-Control": "no-store" };

function error(detail: string, status: number) {
  return Response.json({ detail }, { status, headers });
}

export async function POST(request: Request) {
  const base = process.env.BACKEND_API_URL;
  if (!base) return error("O serviço de cálculo ainda não está configurado.", 503);

  let endpoint: URL;
  try {
    endpoint = new URL("/api/v1/terminations/calculate", base);
    if (endpoint.protocol !== "http:" && endpoint.protocol !== "https:") {
      return error("A configuração do serviço de cálculo é inválida.", 503);
    }
  } catch {
    return error("A configuração do serviço de cálculo é inválida.", 503);
  }

  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return error("Envie os dados do contrato em JSON.", 400);
  }

  const timeout = AbortSignal.timeout(10_000);
  try {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.any([request.signal, timeout]),
    });

    if (response.status !== 200 && response.status !== 400 && response.status !== 422) {
      return error("O serviço de cálculo está indisponível. Tente novamente.", 502);
    }

    return Response.json(await response.json(), { status: response.status, headers });
  } catch {
    if (timeout.aborted) return error("O cálculo demorou demais. Tente novamente.", 504);
    return error("Não foi possível acessar o serviço de cálculo. Tente novamente.", 502);
  }
}
