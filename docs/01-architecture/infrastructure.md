# ☁️ Infraestrutura — SpyFy

## Topologia de nuvem

- **Cloud primária:** AWS (compute, RDS, EKS).
- **Edge/CDN/Storage:** Cloudflare (R2, CDN, WAF, Workers).
- **Multi-região:** us-east-1 (principal), sa-east-1 (BR), eu-west-1 (EU).

## Ambientes

| Ambiente | Uso | Infra |
|----------|-----|-------|
| **local** | Dev | Docker Compose |
| **preview** | PR ephemeral | Namespace K8s por PR |
| **staging** | Homologação | EKS reduzido |
| **production** | Produção | EKS multi-AZ |

## Kubernetes (EKS)

```
Cluster: spyfy-prod
├── namespace: gateway      (api, bff) — 3+ réplicas, HPA
├── namespace: services     (discovery, cloner, intelligence)
├── namespace: workers      (scraper, enrich, transcribe, clone)
├── namespace: data         (redis, temporal, operadores)
└── namespace: observability(prometheus, grafana, loki, tempo)
```

### Autoscaling
- **HPA** por CPU/memória e por profundidade de fila (KEDA para fila-driven).
- **Cluster Autoscaler** / Karpenter para nós.
- Workers de scraping em **spot instances** (tolerantes a interrupção).

## Bancos gerenciados

| Serviço | Provedor | Notas |
|---------|----------|-------|
| PostgreSQL | RDS Aurora | Multi-AZ, read replicas |
| Redis | ElastiCache | Cluster mode |
| ClickHouse | ClickHouse Cloud | OLAP |
| Elasticsearch | OpenSearch (AWS) | Busca |
| Object Storage | Cloudflare R2 | Sem egress fee |

## Rede

```
Internet
  │
  ▼
Cloudflare (WAF, DDoS, CDN)
  │
  ▼
AWS ALB (TLS termination)
  │
  ▼
EKS Ingress (NGINX/Traefik)
  │
  ├─ services (ClusterIP)
  └─ workers (sem exposição pública)
```

- VPC privada; workers e DBs em subnets privadas.
- Egress de scraping via **NAT + pool de proxies residenciais**.
- mTLS entre serviços internos (service mesh: Linkerd/Istio).

## Storage & snapshots

- Assets de anúncios/clones em **R2** com lifecycle (mover snapshots antigos p/ classe fria).
- Estrutura de bucket:
```
r2://spyfy-assets/
  creatives/{ad_id}/...
  snapshots/{ad_id}/{captured_at}/...
  clones/{clone_id}/bundle.zip
```

## Secrets & configuração

- **HashiCorp Vault** (ou AWS Secrets Manager) para segredos.
- Config via **ConfigMaps** + variáveis por ambiente.
- Nunca commitar segredos (scan com gitleaks no CI).

## Custos (estimativa mensal — fase inicial)

| Item | Estimativa |
|------|-----------|
| EKS + nós | $1.500 |
| RDS Aurora | $600 |
| ClickHouse Cloud | $400 |
| OpenSearch | $500 |
| Proxies residenciais | $1.200 |
| R2 Storage | $150 |
| IA (OpenAI/Anthropic/Whisper) | $2.000 |
| **Total aprox.** | **~$6.350/mês** |

## DR (Disaster Recovery)

- **RPO:** 15 min (snapshots contínuos do Aurora).
- **RTO:** 1h (failover multi-AZ + IaC para recriar cluster).
- Backups diários cross-region.
- Runbooks em [observability.md](../08-devops/observability.md).

## IaC

- **Terraform** para infra base (VPC, EKS, RDS, R2, DNS).
- **Helm** para apps.
- **ArgoCD** para GitOps (sync automático do repo `infra/`).

Detalhes em [deployment.md](../08-devops/deployment.md).
