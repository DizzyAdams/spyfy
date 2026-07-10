# 🛡️ Carrinho + Page Builder + Garantia 24h (Loop 9)

Recuperação de carrinho, o **gerador de páginas** e a **garantia matadora**.
Código: `spyfy/cart.py` (testes ✅).

## 1) Recuperação de Carrinho
Detecta checkout não concluído e roda sequência:
**30min → 3h → 24h** (email/SMS/push via A13).

```python
cart = AbandonedCart("c1", "u1", "pro", 49.0, created_at)
i = next_reminder(cart, now)        # proximo lembrete
recover(cart, now) if paid else expire(cart, now)
```
- `next_reminder()` → índice do próximo lembrete (ou None).
- `recover()` → status `recovered`.
- `expire()` → após 24h sem recuperar → `expired`.

## 2) Gerador de Páginas (Page Builder)
> O **nosso gerador** monta a lander do clone **por encomenda**.
> **FLUXO**: ele **envia uma solicitação via email** do que precisa
> (brief) → produz a página → **entrega**.

```python
req = PageRequest("r1", "u1", "ofr_1",
                  "Preciso de lander com VSL e CTA p/ Keto BR")
html = build_page(req, now)   # brief -> HTML entregue
```
Blocos: `headline · video(VSL) · cta · testimonial · offer`.

## 3) 🛡️ GARANTIA (diferencial)
> **Se NÃO ENTREGARMOS em até 24h, o usuário recebe
> 1 ANO GRÁTIS + TODO o valor de volta.**

```python
g = evaluate_guarantee(req, now, paid_usd=588.0)
# dentro do SLA -> g.within_sla=True, refund=0
# FORA 24h       -> g.within_sla=False, refund=588.0, free_months=12
```
- `SLA_SECONDS = 24*3600`.
- Entregue no prazo → sem custo.
- **Atrasou** → reembolso **integral** + **12 meses grátis** (1 ano).
- Pendente ainda no prazo → `within_sla=True` (não punir quem está produzindo).

## Por que converte
- **Zero risco percebido** pro cliente (garantia forte).
- **Força o SLA interno** (time corre pra entregar).
- **Email-brief** = cliente descreve, SpyFy entrega a lander.

## Testado
`test_proxies_crm_cart.py`:
- lembrete 30min; recover; expire 24h.
- página gerada do brief.
- **garantia OK dentro do SLA**; **reembolso 1 ano se atrasa**; pendente ainda no prazo.

## Auditoria da garantia
Cada `PageRequest` registra `created_at`/`delivered_at` →
reconciliação noturna confere SLA e emite crédito automático.
