# 🔐 Autenticação & Billing — SpyFy

## Autenticação

### Provedores
- **Clerk** ou **Auth.js** para login (email/senha, Google, magic link).
- MFA opcional (TOTP).
- SSO/SAML para Enterprise.

### Tokens
- **Access JWT** (curto, 15 min) + **refresh token** (rotativo).
- **API Keys** para server-to-server (`sk_live_...`, `sk_test_...`).
- Scopes por chave: `offers:read`, `clones:write`, etc.

### Sessões
- Sessões em Redis, invalidáveis (logout global).
- Device tracking para segurança.

## Autorização

- **RBAC** por workspace: `owner`, `admin`, `member`, `viewer`.
- **Row-Level Security** por `workspace_id` no Postgres.
- Verificação de scope no Gateway (NestJS Guards).

```ts
@UseGuards(JwtGuard, ScopeGuard('clones:write'))
@Post('/v1/clones')
createClone() { ... }
```

## Multi-tenancy

- Um usuário pode pertencer a múltiplos workspaces.
- Contexto de workspace via header `X-Workspace-Id` ou claim no JWT.

## Billing

### Provedor
- **Stripe** (subscriptions + metered usage).

### Modelo
- Assinatura por plano (Free/Starter/Pro/Agency/Enterprise).
- **Créditos de clonagem** como item metered.
- Add-ons: pacotes de créditos, API extra.

### Fluxo de assinatura
```
1. Usuário escolhe plano → Stripe Checkout.
2. Webhook checkout.session.completed → ativa plano.
3. Webhook invoice.paid → renova.
4. Webhook subscription.deleted → downgrade p/ Free.
```

### Quotas & enforcement
- Quotas por plano cacheadas em Redis.
- Gateway verifica quota antes de operações caras (busca, clone).
- 402/429 quando excede, com upsell.

```json
{
  "error": {
    "code": "quota_exceeded",
    "message": "Limite de clonagens do plano atingido",
    "upgrade_url": "https://app.spyfy.io/billing"
  }
}
```

### Créditos de clonagem
- Cada clone consome 1 crédito.
- Saldo em Postgres, decremento transacional.
- Reclonagem em 24h não recobra (idempotência).

### Webhooks Stripe
```
checkout.session.completed
invoice.paid
invoice.payment_failed
customer.subscription.updated
customer.subscription.deleted
```
- Assinatura verificada (Stripe-Signature).
- Idempotência por event id.

## Segurança de billing

- Nunca confiar no cliente para plano/quota.
- Reconciliação diária Stripe ↔ Postgres.
- Alertas de falha de pagamento (dunning).

## Compliance

- PCI: pagamento via Stripe (não armazenamos cartão).
- LGPD/GDPR: dados pessoais mínimos, direito ao esquecimento.
- Ver [compliance.md](../09-security/compliance.md).

## Métricas

- MRR/ARR, churn, conversão Free→Pro.
- Falha de pagamento, dunning recovery.
- Uso de créditos por plano.
