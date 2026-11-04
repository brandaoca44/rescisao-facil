import Link from "next/link";
import SiteHeader from "./site-header";

const icons = {
  calculator: "M6 2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Zm-2 7h16M9 9v13m6-13v13M4 15h16",
  chart: "M3 13h4v8H3zm7-5h4v13h-4zm7-5h4v18h-4z",
  document: "M6 2h8l5 5v15H6zM14 2v6h5M9 12h7m-7 4h7",
  scales: "M12 2v19m-5 1h10M3 6h18M5 6l-4 9h8L5 6Zm14 0-4 9h8l-4-9Z",
  bolt: "m13 2-9 12h7l-1 8 10-13h-7l1-7z",
  shield: "m12 2 8 4v6c0 5-4 8-8 10-4-2-8-5-8-10V6zM8 12l3 3 5-6",
};

function Icon({ name }: { name: keyof typeof icons }) {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={icons[name]} /></svg>;
}

const steps = [
  { icon: "calculator", title: "Informe seus dados", text: "Preencha um formulário simples e guiado.", href: "/calculadora" },
  { icon: "chart", title: "Calcule o resultado", text: "Veja o valor estimado de cada verba da sua rescisão.", href: "/calculadora" },
  { icon: "document", title: "Confira o detalhamento", text: "Consulte o total bruto, os descontos e o valor líquido.", href: "/calculadora" },
  { icon: "scales", title: "Entenda seus direitos", text: "Veja as condições do FGTS e do seguro-desemprego.", href: "#direitos" },
] as const;

export default function Home() {
  return (
    <main id="inicio">
      <div className="hero">
        <SiteHeader />
        <section className="hero-shell hero-content" aria-labelledby="titulo">
          <p className="hero-kicker">CALCULADORA TRABALHISTA <strong>GRATUITA</strong></p>
          <h1 id="titulo">Calcule sua<br />Rescisão Trabalhista<br />em <em>poucos minutos</em></h1>
          <p className="hero-description">Estime as verbas do seu desligamento de forma simples, rápida e com base nas regras da CLT.</p>
          <Link className="hero-cta" href="/calculadora">
            <Icon name="calculator" /> Calcular minha rescisão <span aria-hidden="true">→</span>
          </Link>
          <ul className="hero-benefits">
            <li><span><Icon name="bolt" /></span>Rápido<br />e prático</li>
            <li><span><Icon name="shield" /></span>100%<br />gratuito</li>
            <li><span><Icon name="document" /></span>Resultado<br />detalhado</li>
          </ul>
        </section>
        <section className="hero-steps" aria-label="Como funciona">
          {steps.map(({ icon, title, text, href }) => (
            <Link key={title} href={href}>
              <span className="step-icon"><Icon name={icon} /></span>
              <span><strong>{title}</strong><span className="step-text">{text}</span></span>
            </Link>
          ))}
        </section>
      </div>
      <section className="shell info-section tutorial" id="como-funciona" aria-labelledby="tutorial-title">
        <p className="eyebrow">PASSO A PASSO</p>
        <h2 id="tutorial-title">Como funciona o cálculo?</h2>
        <div className="tutorial-prep">
          <h3>O que você precisa ter em mãos</h3>
          <p>Separe a Carteira de Trabalho, um holerite recente e, se houver multa do FGTS no seu caso, o extrato com a base para fins rescisórios.</p>
        </div>
        <ol className="tutorial-steps">
          <li><h3>1. Seus dados</h3><p>Informe o salário mensal bruto, as datas de admissão e desligamento e o tipo de desligamento.</p></li>
          <li><h3>2. Contrato</h3><p>Selecione como foi o aviso prévio, quando aplicável. Se foi trabalhado, use o último dia de cumprimento como data de desligamento.</p></li>
          <li><h3>3. Verbas</h3><p>Informe os períodos inteiros de férias pendentes e a base da multa do FGTS, quando solicitada. Se já recebeu parte do décimo terceiro, informe o valor bruto pago e os descontos ou depósitos anteriores.</p></li>
          <li><h3>4. Resultado</h3><p>Clique em “Calcular rescisão” para ver o bruto, os descontos e o líquido estimado. Consulte o FGTS em separado e confira se a data projetada do aviso altera os períodos de férias informados.</p></li>
        </ol>
        <p className="tutorial-scope">A simulação contempla contratos CLT com salário mensal fixo e desligamento em 2026.</p>
        <Link className="tutorial-cta" href="/calculadora">Começar simulação →</Link>
      </section>
      <section className="shell info-section" id="direitos">
        <p className="eyebrow">SEUS DIREITOS</p>
        <h2>Entenda os valores da rescisão</h2>
        <p>O resultado discrimina as verbas, os descontos e as condições associadas à modalidade de desligamento. O FGTS e a multa aparecem em um bloco separado do pagamento direto.</p>
      </section>
      <section className="shell info-section" id="duvidas">
        <p className="eyebrow">DÚVIDAS</p>
        <h2>Perguntas frequentes</h2>
        <details className="history"><summary>Qual salário devo informar?</summary><p className="field-note">Use o salário mensal bruto, antes de INSS, IRRF ou outros descontos.</p></details>
        <details className="history"><summary>Que desligamentos posso simular?</summary><p className="field-note">A calculadora cobre desligamentos em 2026 por dispensa com ou sem justa causa, pedido de demissão ou acordo entre empregado e empregador.</p></details>
      </section>
      <footer className="shell footer">Rescisão Fácil <span>·</span> Simulador trabalhista</footer>
    </main>
  );
}
