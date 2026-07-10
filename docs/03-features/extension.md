# 🧩 Extensão Chrome — SpyFy

## Objetivo

Permitir salvar e clonar anúncios **enquanto o usuário navega** no Facebook, Instagram, TikTok e outras redes — sem sair do fluxo.

## Manifest V3

```json
{
  "manifest_version": 3,
  "name": "SpyFy — Ad Spy & Cloner",
  "version": "1.0.0",
  "permissions": ["activeTab", "storage", "scripting"],
  "host_permissions": [
    "https://*.facebook.com/*",
    "https://*.tiktok.com/*"
  ],
  "background": { "service_worker": "background.js" },
  "action": { "default_popup": "popup.html" },
  "content_scripts": [
    { "matches": ["https://*.facebook.com/*"], "js": ["content.js"] }
  ]
}
```

## Componentes

| Componente | Papel |
|-----------|-------|
| Content script | Injeta botão "Salvar no SpyFy" sobre anúncios. |
| Popup | Login, coleções recentes, busca rápida. |
| Service worker | Auth, chamadas à API, mensageria. |

## Fluxo: salvar anúncio

```
1. Content script detecta anúncio na timeline.
2. Injeta botão "Salvar no SpyFy".
3. Ao clicar → extrai dados visíveis (advertiser, criativo, texto).
4. Envia ao service worker → POST /v1/ads/capture.
5. Backend enriquece e adiciona à library do usuário.
6. Feedback visual (toast).
```

## Captura de dados

- Extrai do DOM: URL do criativo, texto, anunciante, link de destino.
- Envia metadados; backend faz enriquecimento completo (mesma pipeline).
- Deduplica com anúncios já indexados.

## Autenticação

- OAuth via popup (token guardado em `chrome.storage`).
- Service worker anexa Bearer nas chamadas.
- Logout limpa storage.

## Quick actions no popup

- Buscar ofertas (mesmo motor da web).
- Ver coleções recentes.
- Clonar oferta salva.
- Ir para o app web.

## Privacidade

- Só ativa nos domínios permitidos.
- Não coleta navegação do usuário fora de anúncios.
- Dados trafegam via HTTPS; nada armazenado localmente além do token.

## Performance

- Content script leve; observa mutações do DOM com throttle.
- Sem bloquear scroll/render da página.

## Distribuição

- Publicada na Chrome Web Store.
- Atualizações automáticas.
- Versionamento alinhado com a API.

## Roadmap da extensão

- Suporte a mais redes (LinkedIn, X, Pinterest).
- Clonagem direto da extensão.
- Overlay de "longevidade" sobre anúncios na timeline.
- Versão Firefox/Edge.

## Testes

- Unit dos utilitários de extração.
- E2E com Playwright + páginas fixture.
- Teste manual por rede (layouts mudam com frequência).
