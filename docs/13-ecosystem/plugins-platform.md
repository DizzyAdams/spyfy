# 🔌 Plugins & Apps Platform — SpyFy

Plataforma para terceiros estenderem o SpyFy: conectores, automações, dashboards, integrações — tudo sobre o **SpyFy Graph** e eventos.

## Visão

```
Developers/Agências
      │ constroem
      ▼
┌──────────────────────────┐
│  SpyFy Apps (plugins)     │
│  conectores · automações  │
│  dashboards · widgets     │
└───────────┬──────────────┘
            │ usam
   ┌────────▼─────────┐
   │  SpyFy Platform  │
   │  API · Webhooks  │
   │  UI Extensions   │
   │  Graph (GraphQL) │
   └──────────────────┘
```

## Tipos de app

| Tipo | Exemplo |
|------|---------|
| **Conector** | Enviar ofertas para Meta Ads Manager / Google Ads. |
| **Automação** | "Quando oferta escalar, criar tarefa no ClickUp". |
| **Dashboard** | Painel custom embutido no SpyFy. |
| **Widget** | Card extra na tela de detalhe da oferta. |
| **Copilot skill** | Nova capacidade para o Copilot. |
| **Data app** | Exporta o Graph para BI (Looker/Metabase). |

## Manifesto de app

```json
{
  "id": "meta-ads-pusher",
  "name": "Meta Ads Pusher",
  "version": "1.0.0",
  "scopes": ["offers:read", "clones:read"],
  "surfaces": ["offer_detail_widget", "copilot_skill"],
  "webhooks": ["offer.scaling_detected"],
  "oauth": { "redirect": "https://app.example.com/callback" },
  "pricing": { "model": "subscription", "price": 19 }
}
```

## Superfícies de extensão (UI Extensions)

- **Widgets** em telas (offer detail, feed, library).
- **Slots** no Copilot (novas tools/skills).
- **Painéis** full-page (dashboards custom).
- Renderizados em **iframe sandbox** (isolamento/segurança) com SDK de ponte.

## SDK de plugin

```ts
import { createApp, useOffer, onEvent } from "@spyfy/apps";

export default createApp({
  offerDetailWidget({ offer }) {
    return <PushButton onClick={() => pushToMeta(offer.id)} />;
  },
  copilotSkill: {
    name: "push_to_meta",
    async run({ offerId }) { return pushToMeta(offerId); },
  },
});
```

## Eventos (subscrição)

```
offer.discovered
offer.scaling_detected
clone.completed
alert.triggered
listing.sold
```
- Webhooks assinados (HMAC) + retry.
- Event stream (WebSocket) para apps em tempo real.

## Autenticação & permissões

- **OAuth2** para apps agirem em nome do usuário.
- **Scopes** granulares; consentimento explícito na instalação.
- Apps rodam com **least privilege**; sem acesso a dados fora do escopo.

## App Store interna

- Catálogo de apps (grátis/pagos).
- Revenue share (ex.: 80/20 a favor do dev).
- Review de segurança antes de publicar.
- Rating e instalação em 1 clique.

## Segurança de plugins

- Sandbox (iframe + CSP restrito; sem acesso ao DOM do host).
- Revisão de código/manifest para apps na store.
- Rate limit por app.
- Kill switch (desabilitar app problemático).
- Ver [security.md](../09-security/security.md).

## Developer experience

- CLI: `spyfy apps init`, `spyfy apps dev`, `spyfy apps publish`.
- Ambiente sandbox com dados de teste.
- Docs + exemplos + Postman.
- Logs e traces do app no dashboard de dev.

## Governança

- Políticas de uso de dados (não revender dados brutos).
- SLA para apps enterprise.
- Deprecação versionada da API.

## Por que é fora do comum

Abre o SpyFy para uma **economia de desenvolvedores**. Agências constroem suas próprias automações; o produto cresce sem o time central escrever cada integração. É o "Zapier/Slack App Directory" do ad intelligence.
