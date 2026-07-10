# 🛡️ Segurança — SpyFy

## Modelo de ameaças (resumo)

| Ativo | Ameaça | Mitigação |
|-------|--------|-----------|
| Dados de usuários | vazamento | criptografia, RLS, least privilege |
| API | abuso/scraping | rate limit, auth, WAF |
| Segredos | exposição | Vault, OIDC, sem segredo em git |
| Infra | comprometimento | hardening, patching, network policy |
| Billing | fraude | reconciliação Stripe, idempotência |
| Scraping egress | bloqueio/legal | proxies, respeito a ToS |

## Autenticação & autorização

- JWT curto + refresh rotativo; MFA opcional; SSO Enterprise.
- RBAC + Row-Level Security por workspace.
- Scopes por API key.
- Ver [auth-billing.md](../04-backend/auth-billing.md).

## Criptografia

- **Em trânsito:** TLS 1.2+ em tudo; mTLS entre serviços internos.
- **Em repouso:** KMS para DBs, R2/S3 encryption.
- Hashing de senhas (Argon2) — quando aplicável (Clerk gerencia).

## Gestão de segredos

- **HashiCorp Vault** / AWS Secrets Manager.
- Rotação automática.
- CI usa OIDC (sem chaves estáticas).
- Scan de segredos (gitleaks) no CI.

## Segurança de aplicação (AppSec)

- Validação de input (Zod/Pydantic) em todos os boundaries.
- Proteção contra OWASP Top 10 (XSS, SQLi, CSRF, SSRF).
- SSRF: cuidado especial no cloner (fetch de URLs externas em sandbox isolada, allowlist/denylist, sem acesso à rede interna).
- CSP, headers de segurança (HSTS, X-Frame-Options).
- Dependências: Snyk/Dependabot; imagens: Trivy.

## Segurança do Cloner (crítico)

- Fetch de LPs em **sandbox isolada** sem acesso à VPC interna.
- Timeout e limites de recurso.
- Sanitização do HTML clonado (remover scripts maliciosos ao exibir preview).
- Nenhuma execução de JS de terceiros no contexto do app.

## Segurança de infraestrutura

- Network policies (deny-by-default) no K8s.
- Workers e DBs em subnets privadas.
- Pods non-root, read-only FS, seccomp.
- Patching automatizado (imagens base atualizadas).
- WAF/DDoS na borda (Cloudflare).

## Segurança de dados

- PII minimizada e classificada.
- Mascaramento em logs.
- Backups criptografados.
- Direito ao esquecimento (LGPD/GDPR).

## Monitoramento de segurança

- Alertas de acesso anômalo.
- Audit log imutável de ações sensíveis.
- SIEM (logs de segurança centralizados).

## Testes de segurança

- SAST no CI.
- DAST (OWASP ZAP) periódico.
- Pentest anual por terceiro.
- Bug bounty (fase futura).

## Resposta a incidentes

- Plano de IR com severidades.
- On-call de segurança.
- Comunicação e disclosure responsável.
- Post-mortem blameless.

## Hardening checklist

- [ ] MFA para admins.
- [ ] Least privilege IAM.
- [ ] Secrets rotacionados.
- [ ] Dependências sem CVE crítico.
- [ ] Network policies aplicadas.
- [ ] Backups testados.
- [ ] WAF ativo.
- [ ] Audit logs habilitados.
