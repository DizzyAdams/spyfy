// Cliente WebSocket de validação em tempo real do Radar SpyFy.
// Conecta, inscreve e imprime as ofertas (offer.new) assim que chegam.
const ws = new WebSocket("ws://localhost:4000");
let n = 0;
const seen = new Set();

ws.onopen = () => {
  ws.send(
    JSON.stringify({
      type: "subscribe",
      filters: { network: "all", niche: "Todos", country: "all" },
    })
  );
  console.log("WS OPEN — inscrito no Radar");
};

ws.onmessage = (e) => {
  let m;
  try {
    m = JSON.parse(e.data);
  } catch {
    return;
  }
  if (m.type === "hello") {
    console.log("HELLO stats:", JSON.stringify(m.stats));
  } else if (m.type === "offer.new") {
    if (seen.has(m.offer.id)) return;
    seen.add(m.offer.id);
    n++;
    console.log(
      `OFFER #${n}: [${m.offer.network}] ${m.offer.headline} ` +
        `— score ${m.offer.winningScore} | ${m.offer.longevityDays}d | ` +
        `${m.offer.estImpressions} impr`
    );
  }
};

ws.onerror = (e) => console.log("WS ERROR:", e.message || e.error || "unknown");

setTimeout(() => {
  console.log(`\nDONE — ${n} ofertas recebidas em tempo real via WebSocket`);
  try {
    ws.close();
  } catch {}
  process.exit(0);
}, 13000);
