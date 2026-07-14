import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

/**
 * Proxy de health check — a única rota de API next.js do frontend.
 *
 * Em vez de o cliente chamar diretamente a API FastAPI (sujeito a CORS),
 * ele bate aqui, e esta rota faz o fetch server-side. O resultado é
 * entregue na mesma origin, sem necessidade de configurar CORS no backend.
 */
export async function GET() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (!apiUrl) {
    return NextResponse.json({ status: "unconfigured", version: "0.2.0" });
  }

  try {
    const res = await fetch(`${apiUrl}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) throw new Error("Backend unhealthy");
    const data = await res.json();
    return NextResponse.json({ ...data, proxy: true });
  } catch {
    return NextResponse.json({
      status: "backend-offline",
      version: "0.2.0",
      proxy: true,
    });
  }
}
