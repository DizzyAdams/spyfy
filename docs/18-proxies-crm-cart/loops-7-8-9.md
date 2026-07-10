# 🌐 Proxy Pool · CRM · Cart/Page Builder + Garantia (Loops 7/8/9)

Três módulos reais e testados que fecham o produto comercial do SpyFy:
**driblar Cloudflare** (scraping), **CRM integrado** (retenção/venda) e
**recuperação de carrinho + gerador de páginas com garantia 24h**.

## Loop 7 — Proxy Pool anti-Cloudflare (`proxy_pool.py`)
- `ProxyPool` com rotação **round-robin / random / sticky**.
- **Sticky** = mantém o mesmo proxy por sessão → essencial p/ **Cloudflare clearance** (o desafio CF fixa ao IP da sessão).
- **Health check**: latência + taxa de sucesso → `score`; proxy ruim desce.
- **Auto-ban**: ≥ `max_failures` (3) falhas → `banned` (sai do pool).
- Seleção por **região** (país do alvo: BR/US).

```python
pool = ProxyPool([Proxy("http://res:p@1.1.1.1:8000", ProxyType.RESIDENTIAL, "BR")],
                  rotation=Rotation.STICKY)
p = pool.get(region="BR", sticky_id="sess-A")   # fixa p/ CF
# apos usar: pool.report(p, ok=True, latency_ms=120)
```

## Loop 8 — CRM Integrado (`crm.py`)
CRM leve (sem Salesforce): `Contact`, `Deal` (pipeline), `Activity`.
**Sinconiza com o SpyFy**: oferta encontrada → clonada (aha→trial) → venda (paying) → winback (churned→contacted).

```python
crm = CRM()
crm.upsert_contact(Contact("u1","Ana","ana@x.com"))
crm.add_deal(Deal("d1","u1","Keto",Stage.LEAD, 0, "ofr_1"))
crm.on_clone_done("u1","ofr_1","clone_9")   # sobe p/ trial (aha)
crm.on_sale("u1", 96.0)                       # paying + valor
crm.pipeline_summary()  # {'paying':1, 'contacts':1, ...}
```
Stages: `lead → contacted → trial → paying → expanding → churned`.

## Loop 9 — Carrinho + Gerador de Páginas + Garantia (`cart.py`)

### Recuperação de carrinho
- `AbandonedCart` + sequência **30min / 3h / 24h** (email/SMS/push via A13).
- `next_reminder()` calcula o próximo lembrete; `recover()` / `expire()`.

### Gerador de Páginas (Page Builder)
> O "nosso gerador" monta a lander do clone **por encomenda**.
> **FLUXO**: ele **envia uma solicitação via email** do que precisa (brief)
> → produz a página → **entrega**.

```python
req = PageRequest("r1","u1","ofr_1",
                  "Preciso de lander com VSL e CTA p/ Keto BR")
html = build_page(req, time.time())   # brief -> HTML
```

### 🛡️ GARANTIA (diferencial matador)
> **Se não entregarmos em até 24h, o usuário recebe 1 ANO GRÁTIS
> + TODO o valor de volta.**

```python
g = evaluate_guarantee(req, now, paid_usd=588.0)
# dentro do SLA -> g.within_sla=True, reembolso 0
# fora 24h      -> g.within_sla=False, refund=588.0, free_months=12
```
`SLA_SECONDS = 24*3600`. A garantia é **automática** e auditável.

## Como se encaixam (ciclo comercial)

```
Usuario abandona checkout
   └─ Cart Recovery (Loop 9): 30min/3h/24h -> recupera OU expira
Usuario pede clone
   └─ Page Builder envia brief por email -> gera lander (SLA 24h)
        └─ GARANTIA: fora 24h => 1 ano gratis + valor de volta
Usuario vende
   └─ CRM (Loop 8): clone->trial, venda->paying
SpyFy raspa
   └─ Proxy Pool (Loop 7): sticky p/ Cloudflare, auto-ban
```

## Testes (12, todos ✅)
- Proxy: sticky mantém sessão; ban após 3 falhas; filtro por região.
- CRM: lead→paying (valor); winback reativa churned.
- Cart: lembrete 30min; recover; expire 24h.
- Page: gerada do brief; garantia OK dentro do SLA; **reembolso 1 ano se atrasa**; pendente ainda no prazo.

## Vantagem
- **Proxies sticky** = raspagem que não bate no Cloudflare.
- **CRM nativo** = sem integração externa cara.
- **Garantia 24h** = converte indeciso (zero risco percebido) e força o SLA interno.
- **Page builder por email** = usuário descreve, SpyFy entrega a lander.

## Documentos relacionados
- [proxy-guide.md](proxy-guide.md) · [crm-guide.md](crm-guide.md) · [cart-garantia.md](cart-garantia.md)
