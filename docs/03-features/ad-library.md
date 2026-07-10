# 🗂️ Ad Library (Biblioteca de Anúncios) — SpyFy

## Objetivo

Ser o **swipe file colaborativo** definitivo: onde ofertas descobertas são salvas, organizadas, anotadas e compartilhadas com o time.

## Conceitos

| Conceito | Descrição |
|----------|-----------|
| **Coleção** | Pasta temática de ofertas (ex.: "Keto BR — testar"). |
| **Item** | Uma oferta/anúncio salvo numa coleção, com nota. |
| **Tag** | Rótulo livre (ex.: "hook forte", "VSL longa"). |
| **Nota** | Comentário do usuário sobre a oferta. |
| **Alerta** | Regra que notifica quando algo muda. |

## Funcionalidades

- Salvar oferta em uma ou várias coleções.
- Coleções privadas ou compartilhadas (workspace).
- Tags e busca dentro da biblioteca.
- Anotações e menções a colegas.
- Histórico de snapshots por oferta (ver evolução dos criativos).
- Exportar coleção (CSV/PDF/JSON).

## Modelo (resumo)

```
collections (id, workspace_id, name, owner_id, visibility)
collection_items (collection_id, offer_id, note, added_by, added_at)
tags (id, workspace_id, name)
item_tags (item_id, tag_id)
```

## Compartilhamento & permissões

| Papel | Ver | Adicionar | Editar | Excluir |
|-------|-----|-----------|--------|---------|
| Owner | ✅ | ✅ | ✅ | ✅ |
| Editor | ✅ | ✅ | ✅ | ❌ |
| Viewer | ✅ | ❌ | ❌ | ❌ |

- Coleções compartilhadas herdam permissões do workspace.
- Links de compartilhamento read-only (opcional, com expiração).

## Alertas

Tipos:
- **Novo criativo do anunciante X.**
- **Nova oferta no nicho Y ativa > N dias.**
- **Oferta salva mudou de status** (ativou/pausou).
- **Oferta escalando** (winning_score subiu > X%).

Canais: e-mail, Slack, webhook, in-app.

```json
{
  "type": "new_creative",
  "advertiser_id": "adv_55",
  "channel": ["email", "slack"],
  "frequency": "realtime"
}
```

## Histórico de snapshots

- Cada oferta mostra timeline de criativos capturados.
- Diff visual entre versões.
- Útil para ver como o anunciante itera a copy.

## UX

- Grid/lista alternável.
- Drag-and-drop entre coleções.
- Busca + filtros dentro da biblioteca.
- Painel lateral de detalhes ao clicar num item.

## Métricas

- Nº de ofertas salvas por usuário/semana (proxy de WWOA).
- Coleções compartilhadas ativas.
- Alertas criados e taxa de ação sobre alertas.

## Integrações

- Extensão Chrome: salvar direto do FB/TikTok.
- API: listar/exportar coleções programaticamente.
- Slack: alertas e busca via slash command (roadmap).
