import Link from "next/link";
export default function SiteHeader({ calculator = false }: { calculator?: boolean }) {
  return (
    <header className="hero-shell hero-header">
          <Link className="hero-brand" href="/">
            <svg className="hero-monogram" aria-hidden="true" viewBox="0 0 72 70">
              <defs><linearGradient id="brand-purple" x2="0" y2="1"><stop stopColor="#fff0ff"/><stop offset="1" stopColor="#a927ec"/></linearGradient></defs>
              <path fill="url(#brand-purple)" d="M20 6h30c13 0 20 8 17 20-2 9-9 15-18 18l13 19H45L32 45h-9l-5 18H3L20 6Zm11 13-4 13h18c5 0 8-3 9-7 1-4-2-6-6-6H31Z"/>
            </svg>
            <span>Rescisão <em>Fácil</em></span>
          </Link>
          <nav aria-label="Navegação principal">
            <Link className={!calculator ? "hero-home" : undefined} aria-current={!calculator ? "page" : undefined} href="/">Início</Link>
            <Link className={calculator ? "hero-home" : undefined} aria-current={calculator ? "page" : undefined} href="/calculadora">Calculadora</Link>
            <Link href="/#como-funciona">Como funciona</Link>
            <Link href="/#direitos">Seus direitos</Link>
            <Link href="/#duvidas">Dúvidas</Link>
          </nav>
        </header>
  );
}
