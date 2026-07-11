<#
.SYNOPSIS
  Deploy do backend SpyFy (FastAPI) em plataforma FREE (Render ou HuggingFace Spaces).
.DESCRIPTION
  Valida localmente (lint+testes+smoke), depois deploy em free tier.
  - Render: precisa de $env:RENDER_API_KEY (conta free, sem cartão).
  - HuggingFace: precisa de $env:HF_TOKEN (conta free; Spaces Docker 16GB RAM).
  Sem token, apenas valida e imprime o proximo passo (documentado em
  docs/08-devops/backend-deploy.md).
.PARAMETER Platform
  render (padrao) | huggingface
.EXAMPLE
  $env:RENDER_API_KEY='rnd_xxx'; pwsh scripts/deploy-backend.ps1 -Platform render
#>
param(
  [ValidateSet('render', 'huggingface')]
  [string]$Platform = 'render'
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$be = Join-Path $root 'apps/workers-py'

Write-Host "=== SpyFy backend — validacao local ===" -ForegroundColor Cyan
Set-Location $be
python -m pip install -q -r requirements.txt pytest pytest-asyncio
pytest -q
python -c "from spyfy.api.app import create_app; app=create_app(); r=[x.path for x in app.routes]; assert '/health' in r and '/v1/agents/run' in r; print('smoke OK — endpoints:', len(r))"

if ($Platform -eq 'render') {
  if (-not $env:RENDER_API_KEY) {
    Write-Host "`nRENDER_API_KEY nao definido." -ForegroundColor Yellow
    Write-Host "1) Conecte o repo no Render (ele le o render.yaml) — Dashboard > New > Web Service." -ForegroundColor White
    Write-Host "2) Defina WEBHOOK_SECRET (forte) e NTFY_URL nas env vars do service." -ForegroundColor White
    Write-Host "3) Deploy automatico a cada push na main. URL final: https://spyfy-api.onrender.com" -ForegroundColor White
    exit 0
  }
  Write-Host "`n=== Deploy Render ===" -ForegroundColor Cyan
  pip install -q render-cli
  render login --api-key $env:RENDER_API_KEY
  render services deploy --service spyfy-api
  Write-Host "Deploy enviado. Health: https://spyfy-api.onrender.com/health" -ForegroundColor Green
}
else {
  if (-not $env:HF_TOKEN) {
    Write-Host "`nHF_TOKEN nao definido. Crie um Space (Docker) e `huggingface-cli login`." -ForegroundColor Yellow
    exit 0
  }
  Write-Host "`n=== Deploy HuggingFace Space (Docker) ===" -ForegroundColor Cyan
  pip install -q huggingface_hub
  huggingface-cli login --token $env:HF_TOKEN
  # O Dockerfile de apps/workers-py + README de metadata sao usados pelo Space.
  Write-Host "推送 o repo (ou o dir apps/workers-py) para o Space. Veja docs/08-devops/backend-deploy.md" -ForegroundColor White
}
