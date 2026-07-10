# 🤝 CRM Integrado — Guia (Loop 8)

CRM leve **nativo do SpyFy** (sem Salesforce/Pipedrive). Código: `spyfy/crm.py` (testes ✅).

## Modelo
- `Contact` — todo usuário do SpyFy já é um contato.
- `Deal` — pipeline do afiliado/agência (etapas de venda).
- `Activity` — eventos (oferta encontrada, clone, venda, winback).

## Stages (pipeline)
`lead → contacted → trial → paying → expanding → churned`

## Sinconização com o SpyFy
```python
crm = CRM()
crm.upsert_contact(Contact("u1", "Ana", "ana@x.com"))
crm.add_deal(Deal("d1", "u1", "Keto BR", Stage.LEAD, 0, "ofr_1"))

crm.on_offer_found("u1", "ofr_1", "keto")   # activity
crm.on_clone_done("u1", "ofr_1", "clone_9")  # aha -> trial
crm.on_sale("u1", 96.0)                    # paying + valor
crm.winback("u1")                          # churned -> contacted
```

## Webhooks de entrada (NexusTracker/Darkfy)
- `order.paid` (Darkfy) → `crm.on_sale(contact, amount)`.
- `conversion.tracked` (NexusTracker) → atualiza valor do deal.
- `billing.failed` → marca `churned` + dispara winback (A13).

## Handlers (reação a atividades)
```python
def on_activity(a):
    if a.type == ActivityType.WINBACK:
        notify(a.contact_id, "Winback enviado!")
crm.on_activity(on_activity)
```

## Consultas
- `pipeline_summary()` → contagem por stage + # contatos/activities.
- `_deal_for(user)` → deal ativo do usuário.

## Por que integrado
- **Sem custo** de CRM externo.
- **Sem fricção** de sync (eventos já estão no EventBus).
- Retenção/comercial e dados de descoberta **no mesmo lugar**.

## Testado
`test_proxies_crm_cart.py`: lead→paying (valor), winback reativa churned.
