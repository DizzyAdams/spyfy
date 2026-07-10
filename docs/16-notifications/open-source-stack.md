# 🔔 Notification Stack — Projetos Open-Source

O SpyFy usa uma stack **100% open-source e self-hostável** para notificações — sem lock-in de SaaS, com controle total de custo e dados.

## Projetos escolhidos

| Projeto | Papel | Licença | Por quê |
|---------|-------|---------|---------|
| **Novu** | Orquestração + inbox in-app | MIT | Infra completa de notificação (workflows, digest, preferências, inbox). Self-host. |
| **Apprise** | Fan-out multicanal (lib) | BSD-2 | 100+ serviços (Slack, Discord, Telegram, etc.) numa API só. |
| **ntfy.sh** | Push simples (mobile/desktop) | Apache-2 | Push self-host trivial (HTTP → app). |
| **Gotify** | Push server (alternativa) | MIT | Push self-host com app Android próprio. |
| **Postal / Listmonk** | Email transacional/bulk | MIT/AGPL | Envio de email self-host (alternativa a SES). |
| **SMPP gateway** (sim/playsms) | SMS OSS | — | SMS via SMPP self-host (alternativa a Twilio). |
| **FCM / APNs** | Push iOS+Android | — | FCM (Android) / APNs HTTP/2+JWT (iOS). |

## Como se encaixam

```
                 ┌──────────────────────────────┐
                 │  SpyFy Notification Engine     │
                 │  (decide o quê/quem/canais)    │
                 │  spyfy/notifications.py        │
                 └───────────────┬───────────────┘
        ┌────────────┬───────────┼───────────┬───────────────┐
        ▼            ▼           ▼           ▼               ▼
   ┌─────────┐  ┌─────────┐ ┌─────────┐ ┌──────────┐  ┌──────────┐
   │  Novu   │  │ Apprise │ │  ntfy   │ │  Gotify  │  │ Postal/  │
   │ in-app+ │  │ slack/  │ │  push   │ │  push    │  │ Listmonk │
   │ email   │  │ discord/│ │ mobile  │ │  server  │  │ email    │
   │ workflow│  │ telegram│ └─────────┘ └──────────┘  └──────────┘
   └─────────┘  └─────────┘
```

- O **Engine** (nosso, testado) resolve canais por plano/prefs/quiet-hours.
- **Novu** cuida de workflows, digest, in-app inbox e preferências.
- **Apprise** faz o fan-out para chat (Slack/Discord/Telegram/WhatsApp).
- **ntfy/Gotify** entregam push mobile self-host.

## Mapeamento canal → backend

```python
CHANNEL_BACKEND = {
  "in_app": "novu", "email": "novu",
  "push": "ntfy",   # ou gotify
  "slack": "apprise", "discord": "apprise",
  "telegram": "apprise", "whatsapp": "apprise",
  "webhook": "native",
}
```

## Novu (orquestração)

- Self-host via Docker/K8s (Helm chart oficial).
- Workflows: trigger → steps (in-app, email, delay/digest, condições).
- Inbox in-app pronto (componente React `@novu/notification-center`).
- Preferências de usuário e unsubscribe nativos.

```ts
import { Novu } from "@novu/node";
const novu = new Novu(process.env.NOVU_API_KEY, { backendUrl: NOVU_SELFHOST });
await novu.trigger("offer-scaling", {
  to: { subscriberId: user.id, email: user.email },
  payload: { offer: "Keto BR", score: 91 },
});
```

## Apprise (fan-out chat)

```python
import apprise
a = apprise.Apprise()
a.add("slack://TOKEN/CHANNEL")
a.add("discord://WEBHOOK_ID/TOKEN")
a.add("tgram://BOT_TOKEN/CHAT_ID")
a.notify(title="Oferta escalando!", body="Keto BR — score 91")
```

## ntfy (push self-host)

```python
import httpx
httpx.post("https://ntfy.spyfy.io/alerts",
           data="Oferta escalando: Keto BR (91)".encode(),
           headers={"Title": "SpyFy", "Priority": "high", "Tags": "fire"})
```

## Deploy (docker-compose trecho)

```yaml
  novu-api:   { image: ghcr.io/novuhq/novu/api:latest }
  novu-ws:    { image: ghcr.io/novuhq/novu/ws:latest }
  ntfy:       { image: binwiederhier/ntfy, command: serve }
  gotify:     { image: gotify/server }
```

## Vantagens do OSS

- **Zero lock-in** e custo previsível (self-host).
- **Dados sob controle** (LGPD/GDPR).
- **Extensível** (Apprise cobre 100+ serviços).
- **Comunidade ativa** e licenças permissivas.

## Ver também
- [overview.md](overview.md) — arquitetura e fluxo.
- [plans-matrix.md](plans-matrix.md) — canais por plano.
- [channels.md](channels.md) — detalhe por canal.
- Código: `apps/workers-py/spyfy/notifications.py` (11 testes ✅).
