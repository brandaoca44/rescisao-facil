"use client";

import Link from "next/link";
import DateField from "./date-field";
import { useState, type FormEvent } from "react";

import TerminationResult, { type CalculationResult } from "./termination-result";

const modalities = {
  dismissal_without_cause: "Dispensa sem justa causa",
  resignation: "Pedido de demissão",
  mutual_agreement: "Acordo entre empregado e empregador",
  dismissal_with_cause: "Dispensa com justa causa",
};

type Modality = keyof typeof modalities;

const decimalPattern = String.raw`(?:[0-9]{1,10}(?:[,.][0-9]{1,2})?|(?:[0-9]{1,3}(?:\.[0-9]{3}){1,2}|[0-9](?:\.[0-9]{3}){3})(?:,[0-9]{1,2})?)`;
const moneyPattern = String.raw`(?:R\$\s)?` + decimalPattern;
const positiveMoneyPattern = "(?=.*[1-9])" + moneyPattern;
const brl = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

function formatMoney(event: React.FocusEvent<HTMLInputElement>) {
  const input = event.currentTarget;
  if (input.value && input.validity.valid) input.value = brl.format(Number(decimal(input.value)));
}

function editMoney(event: React.FocusEvent<HTMLInputElement>) {
  event.currentTarget.value = event.currentTarget.value.replace(/^R\$\s/, "");
}

const historyFields = ["gross_amount", "inss_withheld", "irrf_withheld", "fgts_deposited"] as const;

function decimal(value: string) {
  value = value.replace(/^R\$\s/, "");
  return value.includes(",") ? value.replaceAll(".", "").replace(",", ".") : value.replace(/\.(?=\d{3}(?:\.|$))/g, "");
}

const fieldLabels: Record<string, string> = {
  monthly_salary: "salário mensal bruto",
  admission_date: "data de admissão",
  termination_date: "data de desligamento",
  termination_type: "modalidade",
  notice_period_type: "aviso prévio",
  acquired_vacation_periods: "férias adquiridas",
  overdue_vacation_periods: "férias vencidas",
  fgts_rescission_base: "base da multa do FGTS",
  gross_amount: "décimo terceiro bruto já pago",
  inss_withheld: "INSS anterior",
  irrf_withheld: "IRRF anterior",
  fgts_deposited: "FGTS anterior",
};

function errorMessage(status: number, detail: unknown) {
  if (status >= 500 && typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const fields = [...new Set(detail.flatMap((issue) => {
      const field = issue?.loc?.at(-1);
      return typeof field === "string" && Object.hasOwn(fieldLabels, field) ? [fieldLabels[field]] : [];
    }))];
    return fields.length ? `Confira os campos: ${fields.join(", ")}.` : "Confira os dados informados e tente novamente.";
  }
  if (typeof detail === "string") {
    if (detail.includes("tables for")) return "Informe um desligamento ocorrido em 2026.";
    if (detail.includes("before admission")) return "A data de desligamento deve ser igual ou posterior à admissão.";
    if (detail.includes("Notice period")) return "Escolha um aviso prévio compatível com a modalidade.";
    if (/vacation|concession period/i.test(detail)) return "Confira a classificação e a quantidade dos períodos de férias na data projetada.";
    if (/thirteenth/i.test(detail)) return "Revise o décimo terceiro bruto já pago e os descontos ou depósitos anteriores. Os valores precisam ser compatíveis com o total apurado.";
  }
  return "Não foi possível calcular a rescisão. Confira os dados e tente novamente.";
}

export default function TerminationForm() {
  const [step, setStep] = useState(0);
  const [modality, setModality] = useState<Modality | "">("");
  const [notice, setNotice] = useState("");
  const [admission, setAdmission] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<CalculationResult | null>(null);
  const showNotice = modality && modality !== "dismissal_with_cause";
  const showFgts = modality === "dismissal_without_cause" || modality === "mutual_agreement";

  async function calculate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;

    const active = event.currentTarget.querySelector("fieldset:not([hidden])");
    for (const input of active?.querySelectorAll<HTMLInputElement | HTMLSelectElement>("input, select") ?? []) {
      if (!input.reportValidity()) return;
    }

    if (step < 2) {
      setStep(step + 1);
      return;
    }

    const data = new FormData(event.currentTarget);
    const read = (name: string) => String(data.get(name) ?? "");
    const history = Object.fromEntries(historyFields.filter((name) => read(name)).map((name) => [name, decimal(read(name))]));
    const payload = {
      monthly_salary: decimal(read("monthly_salary")),
      admission_date: read("admission_date"),
      termination_date: read("termination_date"),
      termination_type: modality,
      acquired_vacation_periods: Number(read("acquired_vacation_periods")),
      overdue_vacation_periods: Number(read("overdue_vacation_periods")),
      ...(showNotice ? { notice_period_type: notice } : {}),
      ...(showFgts && read("fgts_rescission_base") ? { fgts_rescission_base: decimal(read("fgts_rescission_base")) } : {}),
      ...(Object.keys(history).length ? { thirteenth_previous_payment: history } : {}),
    };

    setBusy(true);
    setError("");
    setResult(null);
    try {
      const response = await fetch("/api/terminations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await response.json();
      if (!response.ok) {
        setError(errorMessage(response.status, body.detail));
        return;
      }
      setResult(body);
      setStep(3);
    } catch {
      setError("A conexão falhou. Tente calcular novamente.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="calculator">
    <ol className="wizard-progress" aria-label="Etapas da simulação">
      {["Seus dados", "Contrato", "Verbas", "Resultado"].map((label, index) => (
        <li key={label} aria-current={step === index ? "step" : undefined}>
          <span>{index + 1}</span>{label}
        </li>
      ))}
    </ol>
    <form className="wizard-form" hidden={step === 3} noValidate aria-busy={busy} onSubmit={calculate} onChange={() => { setError(""); setResult(null); }}>
      <fieldset disabled={busy} hidden={step !== 0}>
        <legend>Informações do trabalhador</legend>
        <div className="field-grid">
          <label>Salário mensal bruto <span>*</span><input name="monthly_salary" required inputMode="decimal" onBlur={formatMoney} onFocus={editMoney} placeholder="Ex.: 3.000,00" pattern={positiveMoneyPattern} title="Informe um salário positivo em reais, com até duas casas decimais." /></label>
          <DateField label="Data de admissão" name="admission_date" max="2026-12-31" onDateChange={setAdmission} />
          <DateField label="Data de desligamento" name="termination_date" min={admission > "2026-01-01" ? admission : "2026-01-01"} max="2026-12-31" />
          <label>Tipo de desligamento <span>*</span>
            <select name="termination_type" value={modality} required onChange={(event) => { setModality(event.target.value as Modality | ""); setNotice(""); }}>
              <option value="">Selecione a modalidade</option>
              {Object.entries(modalities).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
        </div>
        <p className="wizard-tip"><strong>Dica.</strong> Consulte as datas na Carteira de Trabalho e o salário bruto no holerite.</p>
      </fieldset>
      <fieldset disabled={busy} hidden={step !== 1}>
        <legend>Contrato e aviso prévio</legend>
        <p className="field-note" id="date-hint">{notice === "worked" ? "Confira se a data informada é o último dia de cumprimento do aviso." : "Informe a data efetiva do desligamento, antes de eventual projeção do aviso."}</p>
        {!showNotice && <p className="wizard-tip">A modalidade selecionada dispensa o preenchimento do aviso prévio.</p>}
        <div className="field-grid">
          {showNotice && <label className="full">Situação do aviso prévio <span>*</span>
            <select name="notice_period_type" required value={notice} onChange={(event) => setNotice(event.target.value)}>
              <option value="">Selecione a situação</option>
              <option value="worked">Trabalhado</option>
              {modality === "resignation" ? <option value="not_worked">Não cumprido, com desconto</option> : <option value="indemnified">Indenizado</option>}
            </select>
          </label>}
        </div>
      </fieldset>
      <fieldset disabled={busy} hidden={step !== 2}>
        <legend>Férias e outras verbas</legend>
        <p className="field-note" id="vacation-hint">Informe os períodos integrais pendentes na data projetada do desligamento. Cada período entra em uma única categoria.</p>
        <div className="field-grid">
          <label>Férias adquiridas<input name="acquired_vacation_periods" type="number" min="0" step="1" placeholder="0" aria-describedby="vacation-hint" /></label>
          <label>Férias vencidas<input name="overdue_vacation_periods" type="number" min="0" step="1" placeholder="0" aria-describedby="vacation-hint" /></label>
          {showFgts && <label className="full">Base para a multa do FGTS<input name="fgts_rescission_base" inputMode="decimal" onBlur={formatMoney} onFocus={editMoney} pattern={moneyPattern} title="Informe um valor em reais com até duas casas decimais." placeholder="Ex.: 10.000,00" /><small>Consulte a base para fins rescisórios no extrato do FGTS.</small></label>}
        </div>
        {modality !== "dismissal_with_cause" && <details className="history">
          <summary>Décimo terceiro já pago <span>Opcional</span></summary>
          <p className="field-note">Informe somente valores do ano do desligamento. Use o bruto antes dos descontos.</p>
          <div className="field-grid">
            <label>Valor bruto já pago<input name="gross_amount" inputMode="decimal" onBlur={formatMoney} onFocus={editMoney} pattern={moneyPattern} title="Informe um valor em reais com até duas casas decimais." placeholder="0,00" /></label>
            <label>INSS já descontado<input name="inss_withheld" inputMode="decimal" onBlur={formatMoney} onFocus={editMoney} pattern={moneyPattern} title="Informe um valor em reais com até duas casas decimais." placeholder="0,00" /></label>
            <label>IRRF já retido<input name="irrf_withheld" inputMode="decimal" onBlur={formatMoney} onFocus={editMoney} pattern={moneyPattern} title="Informe um valor em reais com até duas casas decimais." placeholder="0,00" /></label>
            <label>FGTS já depositado<input name="fgts_deposited" inputMode="decimal" onBlur={formatMoney} onFocus={editMoney} pattern={moneyPattern} title="Informe um valor em reais com até duas casas decimais." placeholder="0,00" /></label>
          </div>
        </details>}
      </fieldset>
      <div className="wizard-actions">
        {step === 0 ? <Link href="/">← Voltar</Link> : <button type="button" disabled={busy} onClick={() => { setError(""); setStep(step - 1); }}>← Voltar</button>}
        <button type="submit" disabled={busy}>{busy ? "Calculando…" : step === 2 ? "Calcular rescisão" : "Próximo"} <span aria-hidden="true">→</span></button>
      </div>
      {error && <p role="alert" className="form-error">{error}</p>}
    </form>
    <div aria-live="polite">
      {step === 3 && result && <>
        <TerminationResult result={result} />
        <div className="wizard-actions"><button type="button" onClick={() => setStep(2)}>← Revisar verbas</button></div>
      </>}
    </div>
    </div>
  );
}
