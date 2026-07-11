import type { Metadata, Viewport } from "next";
import "./globals.css";
import { CursorAura } from "@/components/illustrations/CursorAura";

export const metadata: Metadata = {
  metadataBase: new URL("https://spyfyprod.vercel.app"),
  title: {
    default: "SpyFy — Inteligência de anúncios e clonagem de ofertas",
    template: "%s · SpyFy",
  },
  description:
    "SpyFy localiza, decodifica e reconstroi ofertas vencedoras de tráfego pago. Reúne discovery, clonagem de criativos e analytics de funil em um único console — para media buyers, afiliados e agências que escalam com dados, não achismo.",
  openGraph: {
    title: "SpyFy — Inteligência de anúncios e clonagem de ofertas",
    description:
      "Localize ofertas vencedoras, reconstrua funis e valide campanhas com dados reais — em minutos, não semanas.",
    type: "website",
    locale: "pt_BR",
  },
};

export const viewport: Viewport = {
  themeColor: "#06070B",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark font-display">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <CursorAura />
        {children}
      </body>
    </html>
  );
}
