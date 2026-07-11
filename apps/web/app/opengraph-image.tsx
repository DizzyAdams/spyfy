import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt =
  "SpyFy — Inteligência de anúncios e clonagem de ofertas com IA";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px",
          backgroundColor: "#06070B",
          color: "#EAECF2",
          fontFamily: "sans-serif",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Volumetric plasma field */}
        <div
          style={{
            position: "absolute",
            top: "-260px",
            left: "-200px",
            width: "720px",
            height: "720px",
            borderRadius: "9999px",
            background:
              "radial-gradient(circle, rgba(124,92,255,0.55), transparent 65%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: "120px",
            right: "-260px",
            width: "700px",
            height: "700px",
            borderRadius: "9999px",
            background:
              "radial-gradient(circle, rgba(45,212,255,0.42), transparent 65%)",
          }}
        />

        {/* Wordmark */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "14px",
            zIndex: 1,
          }}
        >
          <div
            style={{
              width: "34px",
              height: "34px",
              borderRadius: "9px",
              background: "linear-gradient(135deg,#2DD4FF,#7C5CFF)",
              display: "flex",
            }}
          />
          <div
            style={{
              fontSize: "34px",
              fontWeight: 700,
              letterSpacing: "-0.02em",
            }}
          >
            Spy<span style={{ color: "#2DD4FF" }}>Fy</span>
          </div>
        </div>

        {/* Headline */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "18px",
            zIndex: 1,
          }}
        >
          <div
            style={{
              fontSize: "74px",
              fontWeight: 700,
              lineHeight: 1.05,
              letterSpacing: "-0.02em",
              maxWidth: "920px",
            }}
          >
            Encontre a oferta{" "}
            <span
              style={{
                background:
                  "linear-gradient(92deg,#A78BFA,#7C5CFF,#2DD4FF)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                color: "transparent",
              }}
            >
              vencedora
            </span>{" "}
            e reconstrua o funil.
          </div>
          <div
            style={{
              fontSize: "30px",
              color: "#8A90A2",
              maxWidth: "820px",
            }}
          >
            Ad intelligence + offer cloning com IA — sinal do ruído em tempo
            real.
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: "flex", gap: "56px", zIndex: 1 }}>
          {[
            ["2.4B+", "anúncios indexados"],
            ["<60s", "clone de funil"],
            ["95%", "fidelidade"],
          ].map(([n, l]) => (
            <div
              key={l}
              style={{ display: "flex", flexDirection: "column" }}
            >
              <div
                style={{ fontSize: "46px", fontWeight: 700, color: "#EAECF2" }}
              >
                {n}
              </div>
              <div style={{ fontSize: "22px", color: "#8A90A2" }}>{l}</div>
            </div>
          ))}
        </div>
      </div>
    ),
    { ...size },
  );
}
