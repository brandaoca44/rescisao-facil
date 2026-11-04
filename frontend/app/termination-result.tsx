export type CalculationResult = {
  total: string;
  net_total: string;
  salary_balance: string;
  notice_period_value: string;
  notice_period_discount: string;
  projected_termination_date: string;
  thirteenth_salary: string;
  thirteenth_salary_by_year: { year: number; accrued_months: number; value: string }[];
  thirteenth_settlement: { gross_paid: string; gross_balance: string };
  proportional_vacation: string;
  proportional_vacation_bonus: string;
  acquired_vacation: string;
  acquired_vacation_bonus: string;
  overdue_vacation: string;
  overdue_vacation_bonus: string;
  inss_total: string;
  irrf_total: string;
  fgts_termination_deposit: string;
  fgts_penalty: string;
  benefits: {
    fgts_withdrawal_rate_under_saque_rescisao: string;
    unemployment_insurance_possible_by_termination_type: boolean;
    notes: string[];
  };
};

const currency = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const percentage = new Intl.NumberFormat("pt-BR", { style: "percent" });

function Amounts({ rows }: { rows: [string, string][] }) {
  return <dl className="amounts">{rows.map(([label, value]) => (
    <div key={label}><dt>{label}</dt><dd>{currency.format(Number(value))}</dd></div>
  ))}</dl>;
}

export default function TerminationResult({ result }: { result: CalculationResult }) {
  const settlement = result.thirteenth_settlement;
  return (
    <section className="form-card result-card" aria-labelledby="result-title">
      <p className="eyebrow">RESULTADO DA SIMULAÇÃO</p>
      <h2 id="result-title">Total líquido estimado</h2>
      <p className="net-value">{currency.format(Number(result.net_total))}</p>
      {Number(result.net_total) < 0 && <p className="field-note">Os descontos superaram as verbas neste cenário. O saldo da simulação não determina uma cobrança.</p>}
      <Amounts rows={[["Total bruto", result.total]]} />
      <p className="field-note">Data de desligamento considerada para a projeção: {result.projected_termination_date.split("-").reverse().join("/")}. Revise os períodos de férias usando essa data.</p>
      <details open className="history">
        <summary>Verbas da rescisão</summary>
        <Amounts rows={[
          ["Saldo de salário", result.salary_balance],
          ["Aviso indenizado", result.notice_period_value],
          ["Décimo terceiro bruto", result.thirteenth_salary],
          ["Férias proporcionais", result.proportional_vacation],
          ["Terço das férias proporcionais", result.proportional_vacation_bonus],
          ["Férias adquiridas", result.acquired_vacation],
          ["Terço das férias adquiridas", result.acquired_vacation_bonus],
          ["Férias vencidas", result.overdue_vacation],
          ["Terço das férias vencidas", result.overdue_vacation_bonus],
        ]} />
      </details>
      <details className="history">
        <summary>Descontos e décimo terceiro</summary>
        <Amounts rows={[
          ["INSS", result.inss_total], ["IRRF", result.irrf_total],
          ["Desconto do aviso", result.notice_period_discount],
          ["Décimo terceiro bruto já pago", settlement.gross_paid],
          ["Saldo bruto do décimo terceiro", settlement.gross_balance],
          ...result.thirteenth_salary_by_year.map(({ year, accrued_months, value }): [string, string] => [
            `Décimo terceiro de ${year} (${accrued_months}/12)`, value,
          ]),
        ]} />
      </details>
      <details className="history">
        <summary>FGTS e direitos informativos</summary>
        <Amounts rows={[["Depósito rescisório", result.fgts_termination_deposit], ["Multa do FGTS", result.fgts_penalty]]} />
        <p className="field-note">Esses valores ficam separados do pagamento direto da rescisão.</p>
        <p className="field-note">Percentual na sistemática saque-rescisão: {percentage.format(Number(result.benefits.fgts_withdrawal_rate_under_saque_rescisao))}.</p>
        <p className="field-note">{result.benefits.unemployment_insurance_possible_by_termination_type
          ? "A modalidade pode permitir solicitar seguro-desemprego."
          : "A modalidade não habilita a solicitação de seguro-desemprego."}</p>
        <ul className="benefit-notes">{result.benefits.notes.map((note) => <li key={note}>{note}</li>)}</ul>
      </details>
    </section>
  );
}
