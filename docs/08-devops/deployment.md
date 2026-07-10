# 🚀 Deploy & Infra as Code — SpyFy

## Stack de deploy

- **Terraform** — infra base (VPC, EKS, RDS, R2, DNS, IAM).
- **Helm** — empacotamento de apps.
- **ArgoCD** — GitOps (sync do repo `infra/`).
- **KEDA** — autoscaling por fila.

## Estrutura IaC

```
infra/
├── terraform/
│   ├── modules/ (vpc, eks, rds, redis, r2, iam)
│   └── envs/ (staging, production)
├── helm/
│   ├── charts/ (api, workers, web, temporal)
│   └── values/ (staging.yaml, production.yaml)
└── argocd/
    └── apps/ (application manifests)
```

## Terraform (exemplo de módulo)

```hcl
module "eks" {
  source          = "../modules/eks"
  cluster_name    = "spyfy-${var.env}"
  node_groups     = var.node_groups
  spot_workers    = true
  kubernetes_version = "1.30"
}
```

## Helm (values por serviço)

```yaml
api:
  replicaCount: 3
  resources:
    requests: { cpu: 250m, memory: 512Mi }
    limits:   { cpu: 1,    memory: 1Gi }
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20
    targetCPUUtilizationPercentage: 65
```

## Autoscaling de workers (KEDA)

```yaml
triggers:
  - type: redis
    metadata:
      listName: queue:scrape
      listLength: "50"   # 1 réplica por 50 jobs pendentes
```

## Deploy do banco

- Migrations aplicadas por Job pré-deploy.
- Expand/contract (sem downtime).
- Rollback testado em staging.

## DNS & TLS

- Cloudflare DNS + certificados (cert-manager/Let's Encrypt).
- WAF e rate limit na borda.

## Configuração

- ConfigMaps por ambiente.
- Segredos via Vault Agent Injector / External Secrets.
- Nada de segredo em git.

## Estratégia multi-região

- Produção primária us-east-1.
- Réplicas de leitura e edge cache por região.
- Failover documentado em runbooks.

## Runbooks de deploy

1. Verificar CI verde + evals.
2. Merge → ArgoCD sync staging.
3. Smoke tests staging.
4. Promover para produção (canary).
5. Monitorar dashboards por 30 min.
6. Rollback se erro > threshold.

## DR (Disaster Recovery)

- RPO 15 min / RTO 1h.
- IaC permite recriar cluster do zero.
- Backups cross-region testados trimestralmente (game day).

## Custos & FinOps

- Tags de custo por serviço/ambiente.
- Spot para workers, savings plans para baseline.
- Dashboards de custo (Grafana + Cost Explorer).
