import Link from "next/link";
import { Logo } from "./illustrations/Logo";

const cols = [
  {
    title: "Produto",
    links: [
      { label: "Discovery", href: "/#recursos" },
      { label: "Offer Cloner", href: "/#recursos" },
      { label: "Analytics", href: "/app/analytics" },
      { label: "Preços", href: "/#precos" },
    ],
  },
  {
    title: "Recursos",
    links: [
      { label: "Abrir o app", href: "/app/feed" },
      { label: "Comparativo", href: "/#comparativo" },
      { label: "Como funciona", href: "/#como-funciona" },
      { label: "FAQ", href: "/#faq" },
    ],
  },
  {
    title: "Empresa",
    links: [
      { label: "Visão", href: "/" },
      { label: "Segurança & Compliance", href: "/#comparativo" },
      { label: "Status", href: "/" },
      { label: "Contato", href: "/" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border/70 bg-surface/40">
      <div className="mx-auto grid max-w-7xl gap-10 px-5 py-14 md:grid-cols-[1.4fr_repeat(3,1fr)]">
        <div>
          <Logo />
          <p className="mt-4 max-w-xs text-sm text-muted">
            A biblioteca definitiva para encontrar, analisar e clonar ofertas vencedoras — em minutos, não semanas.
          </p>
          <div className="mt-4 flex gap-2">
            <span className="chip">pt-BR</span>
            <span className="chip">LGPD-ready</span>
            <span className="chip">99.9% uptime</span>
          </div>
        </div>
        {cols.map((c) => (
          <div key={c.title}>
            <h4 className="text-sm font-semibold text-text">{c.title}</h4>
            <ul className="mt-3 space-y-2 text-sm">
              {c.links.map((l) => (
                <li key={l.label}>
                  <Link href={l.href} className="text-muted transition-colors hover:text-text">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="hairline" />
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-5 py-6 text-xs text-muted md:flex-row">
        <span>© 2026 SpyFy. Todos os direitos reservados.</span>
        <span>Feito para media buyers, afiliados e agências que escalam.</span>
      </div>
    </footer>
  );
}
