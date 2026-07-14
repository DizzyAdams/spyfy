import { NextResponse } from "next/server";

// Health probe consumido por <BackendStatus> (Navbar/Footer). Faz um GET no
// backend real e reflete online/offline. Nunca quebra a página — degrada para
// "offline" graciosamente. Backend estável em spyfyv1prod.vercel.app.
export const dynamic = "force-dynamic";

const FALLBACK_API = "https://spyfyv1prod.vercel.app";

export async function GET() {
  const base = (process.env.NEXT_PUBLIC_API_URL || FALLBACK_API).replace(/\/+$/, "").trim();
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 9000);
    const res = await fetch(`${base}/health`, { cache: "no-store", signal: ctrl.signal });
    clearTimeout(t);
    if (res.ok) {
      let version = "";
      try {
        const data = await res.json();
        version = data.version || data.commit || "";
      } catch {
        /* body não-JSON: ignora */
      }
      return NextResponse.json({ status: "ok", version });
    }
    return NextResponse.json({ status: "offline", version: "" });
  } catch {
    return NextResponse.json({ status: "offline", version: "" });
  }
}
