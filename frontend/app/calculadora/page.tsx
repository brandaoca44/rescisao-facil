import type { Metadata } from "next";
import SiteHeader from "../site-header";
import TerminationForm from "../termination-form";

export const metadata: Metadata = { title: "Calculadora de Rescisão Trabalhista | Rescisão Fácil" };

const resultItems = [
  "Saldo de salário",
  "Aviso prévio, quando aplicável",
  "Férias + 1/3",
  "Décimo terceiro proporcional",
  "FGTS e multa, quando aplicável",
  "Total líquido estimado",
];

export default function CalculatorPage() {
  return (
    <main className="calculator-page">
      <SiteHeader calculator />
      <div className="calc-shell">
        <section className="calc-intro" aria-labelledby="calc-title">
          <h1 id="calc-title">Calculadora de Rescisão <em>Trabalhista</em></h1>
          <p>Preencha as informações abaixo e veja a estimativa das suas verbas rescisórias.</p>
        </section>
        <div className="calc-grid">
          <TerminationForm />
          <aside className="calc-aside" aria-label="Sobre o cálculo">
            <section className="calc-highlight">
              <span className="calc-illustration" aria-hidden="true">
                <svg viewBox="0 0 80 94" fill="none"><rect x="4" y="4" width="72" height="86" rx="12" fill="#590c96" stroke="#d388ff" strokeWidth="5"/><rect x="15" y="15" width="50" height="23" rx="4" fill="#dfb3ff"/><path d="M18 51h12m-6-6v12m22-6h12M18 72h12m16-4h12m-12 8h12" stroke="#eed3ff" strokeWidth="5" strokeLinecap="round"/></svg>
              </span>
              <div><h2>Cálculo completo<br />e detalhado</h2>
                <ul><li>Verbas por modalidade</li><li>Tabelas de 2026</li><li>Descontos discriminados</li></ul>
              </div>
            </section>
            <section className="calc-expect">
              <h2><span aria-hidden="true">?</span> O que você vai receber no resultado?</h2>
              <ul>{resultItems.map((item) => <li key={item}><span aria-hidden="true">✓</span>{item}</li>)}</ul>
            </section>
          </aside>
        </div>
      </div>
    </main>
  );
}
