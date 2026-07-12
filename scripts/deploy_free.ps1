# Deploy FREE da SpyFy API — sobe o servidor (uvicorn) + tunel cloudflared.
# Resultado: URL publica https://*.trycloudflare.com (efemera, sem conta).
# Para deploy persistente em free tier, use Coolify (docker compose) ou Render
# (render.yaml) — veja docs/08-devops/.
$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..' 'apps/workers-py')
Set-Location $root
$env:PYTHONPATH = '.'

Write-Host '[SpyFy] Subindo API (uvicorn :8000)...'
$uv = Start-Process -PassThru python -ArgumentList '-m', 'uvicorn', 'spyfy.api.app:app', '--host', '0.0.0.0', '--port', '8000'
Start-Sleep -Seconds 4

Write-Host '[SpyFy] Abrindo tunel cloudflared (URL publica)...'
$cf = Start-Process -PassThru cloudflared -ArgumentList 'tunnel', '--url', 'http://localhost:8000'

Write-Host '[SpyFy] API ao vivo. A URL aparece no log do cloudflared acima.'
Write-Host '[SpyFy] Pressione Ctrl+C para encerrar.'
try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    $uv, $cf | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host '[SpyFy] deploy encerrado.'
}
