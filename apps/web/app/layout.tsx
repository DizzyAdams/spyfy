import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SpyFy — Ad Intelligence & Offer Cloning",
  description:
    "Encontre, analise e clone ofertas vencedoras de anúncios em minutos. Longevidade real, reconstrução de funil e IA agentic.",
  metadataBase: new URL("https://spyfy.io"),
  openGraph: {
    title: "SpyFy — Ad Intelligence & Offer Cloning",
    description:
      "A biblioteca definitiva para encontrar, analisar e clonar ofertas vencedoras de anúncios.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
