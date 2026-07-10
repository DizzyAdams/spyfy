# 📧 Email · SMS · Mobile Push (Loop 6) — SpyFy

Novos canais de notificação, todos **open-source / self-host**, plugados no Dispatcher já testado. Código em `apps/workers-py/spyfy/channels.py` (9 testes ✅).

## Canais adicionados

| Canal | Backend OSS | What/Como | Licença |
|-------|-------------|---------------|---------|
| **Email** | **Postal** | transacional/bulk via HTTP API (`/api/v1/send/message`) | AGPL |
| **SMS** | **SMPP gateway** (ex.: SMPP sim) | JSON `{to,text}` p/ gateway OSS | — |
| **Mobile Push** | **ntfy** (Android) | POST `/{topic}` com Title/Priority | Apache-2 |
| | **Gotify** | self-host push server | — | MIT |
| | **FCM** (Android) | `fcm.googleapis.com` | — | — |
| | **APNs** (iOS) | HTTP/2 + JWT (pacote apns2) | — | — |

> Apprise continua cobrindo **Slack/Discord/Telegram/WhatsApp** via URLs configuradas.

## Mapeamento atual (`CHANNEL_BACKEND`)

```python
Channel.IN_APP: "novu"      # in-app inbox (Novu)
Channel.EMAIL:  "postal"    # Postal (self-host)
Channel.SMS:    "sms"       # SMPP gateway OSS
Channel.PUSH:   "mobile"     # ntfy/Gotify/FCM/APNs
Channel.SLACK/DISCORD/TELEGRAM/WHATSAPP: "apprise"
Channel.WEBHOOK: "native"
```

## Email — Postal (self-host)

```python
from spyfy.channels import EmailAdapter
a = EmailAdapter(base_url="https://postal.spyfy.io", api_key=POSTAL_KEY)
a.send(Channel.EMAIL, {"email": "u@x.com"}, notif)   # HTML com unsubscribe
```
Template HTML responsivo com link **unsubscribe** (LGPD/GDPR). DKIM/SPF/DMARC no Postal.

## SMS — SMPP gateway OSS

```python
from spyfy.channels import SmsAdapter
a = SmsAdapter()                       # usa gateway SMPP OSS
a.send(Channel.SMS, {"phone": "+1199991234"}, notif)
# ou via Apprise (twilio://) se preenchido apprise_url
```
Telefone normalizado (`_norm_phone`): mantém só dígitos, ≥10, prefixa `+`.

## Mobile Push (iOS/Android)

```python
from spyfy.channels import MobilePushAdapter
a = MobilePushAdapter(ntfy_url="https://ntfy.spyfy.io",
                         fcm_server_key=FCM_KEY)
# tenta, em ordem: ntfy (Android) → Gotify → FCM (Android) → APNs (iOS)
a.send(Channel.PUSH, {
    "ntfy_topic": "user-u1",    # Android (ntfy app)
    "gotify_url": "...",          # opcional
    "fcm_token": "tk",           # Android (FCM)
    "apns_token": "apns-1",      # iOS (APNs, pacote apns2 em prod)
}, notif)
```
- **iOS**: APNs usa HTTP/2 + token JWT (pacote `apns2` em produção; stub marca intent).
- **Android**: ntfy (app próprio) ou FCM (legacy).
- Prioridade do push herda `notif.priority` (low/default/high/urgent).

## Fluxo E2E (testado)

```
evento → A13 NotifyAgent → Dispatcher
   plano ∩ prefs  →  [in_app, email, sms, push, ...]
        ▼
   Postal(SMS) · SMPP(SMS) · ntfy/FCM/APNs(push)
```
Teste `test_e2e_event_to_email_sms_push` prova entrega em **email + SMS + push** a partir de um evento.

## Segurança & compliance

- Segredos (Postal key, FCM key) no Vault/env.
- Unsubscribe em todo email (opt-out).
- SMS com opt-in; prioridade/horário respeitados.
- Push APNs/FCM: tokens nunca logados.

## Cobertura de testes (9)

- Email: POST ao Postal; exige email; HTML.
- SMS: exige phone; normaliza `+`; trunca 160 chars.
- Mobile: ntfy (topic); FCM (token); APNs stub; Gotify.
- Dispatcher roteia email+sms+push (plano agency).
- E2E evento → email+sms+push entregues.

## Próximos passos

- Conectar `EmailAdapter`/`MobilePushAdapter` ao **Apprise** como fallback automático.
- Template de email via serviço de templates (ex.: Jinja/MJML).
- APNs real (pacote `apns2`) em produção iOS.
