# ⚖️ Compliance & Legal — SpyFy

> **Disclaimer:** este documento é orientação de engenharia, não aconselhamento jurídico. Validar com advogado especializado.

## Filosofia

O SpyFy opera sobre **dados publicamente disponíveis** (bibliotecas de transparência de anúncios) e entrega **inteligência competitiva legítima**. Priorizamos ética, transparência e conformidade.

## Fontes de dados — base legal

| Fonte | Natureza | Consideração |
|-------|----------|--------------|
| Meta Ad Library | Pública (transparência) | Uso de dados públicos; respeitar ToS/API. |
| Google Ads Transparency | Pública | Idem. |
| TikTok Creative Center | Pública | Idem. |
| Landing pages | Públicas | Acesso a páginas públicas; sem áreas logadas. |

- Coletamos **anúncios e páginas públicas**, não dados privados.
- **Não** contornamos autenticação/paywalls.
- Respeitamos `robots.txt` e ToS configuráveis por fonte.

## LGPD / GDPR

- **Dados pessoais tratados:** dados de usuários da plataforma (nome, email, billing).
- **Base legal:** execução de contrato + legítimo interesse.
- **Direitos:** acesso, correção, exclusão (esquecimento), portabilidade.
- **DPO:** designado; canal de privacidade.
- **DPA:** disponível para clientes Enterprise.
- **Transferência internacional:** SCCs quando aplicável.
- **Retenção:** mínima necessária; exclusão automática após churn + período legal.

### Dados de anúncios e privacidade
- Anúncios são conteúdo público; **não** coletamos PII de usuários finais que interagiram com os anúncios.
- Anonimização/agregação em métricas.

## Direitos autorais & marcas (Cloner)

- Clonagem é ferramenta de **estudo, referência e inspiração**.
- Avisos no produto sobre respeito a direitos autorais e marcas.
- Usuário é responsável por não plagiar/violar direitos ao usar clones.
- Takedown: processo para remover conteúdo mediante notificação (DMCA-like).
- Não hospedamos clones publicamente por padrão (privado ao usuário).

## Termos de Uso & Política Aceitável

- Proibido: uso para fraude, phishing, cópia idêntica com má-fé, violação de marcas.
- Direito de suspender contas que violem.

## PCI DSS

- Pagamentos via **Stripe**; não armazenamos dados de cartão (SAQ-A).

## SOC 2 (roadmap)

- Trilha para SOC 2 Type II: controles de acesso, change management, monitoramento, IR.
- Auditoria planejada após maturidade.

## Cookies & tracking

- Banner de consentimento (LGPD/GDPR).
- Analytics com anonimização de IP.

## Governança de dados

- Classificação de dados (público, interno, confidencial, PII).
- Políticas de retenção e exclusão documentadas.
- Audit logs de acesso a dados sensíveis.

## Ética de IA

- Estimativas rotuladas como tal (não fatos).
- Sem geração de conteúdo enganoso.
- Auditoria de viés em modelos.

## Checklist de compliance

- [ ] Política de Privacidade publicada.
- [ ] Termos de Uso publicados.
- [ ] DPA disponível (Enterprise).
- [ ] Fluxo de exclusão de dados.
- [ ] Consentimento de cookies.
- [ ] Processo de takedown.
- [ ] Respeito a ToS das fontes.
- [ ] DPO designado.
