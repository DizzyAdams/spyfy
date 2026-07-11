# Prova ponta-a-ponta: sobe backend (job) + tunnel Cloudflare (job),
# captura a URL publica e valida os endpoints pela internet. Tudo em <30s.
$ErrorActionPreference = 'Continue'
$root = 'C:\Users\forrydev\Desktop\SpyFy'
$cf = 'C:\Users\forrydev\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe'
$log = "$root\cloudflared_tunnel.log"
$tunnelJson = "$root\cloudflared.json"

# limpa jobs/tunnel anteriores
Get-Job | Remove-Job -Force -ErrorAction SilentlyContinue
Remove-Item $log, $tunnelJson -ErrorAction SilentlyContinue

# 1) backend
Start-Job -ScriptBlock {
  Set-Location 'C:\Users\forrydev\Desktop\SpyFy\apps\workers-py'
  $env:PYTHONPATH = '.'
  $env:WEBHOOK_SECRET = 'spyfy-prod-validation'
  & python -m uvicorn spyfy.api.app:app --host 0.0.0.0 --port 8000 *> 'C:\Users\forrydev\Desktop\SpyFy\apps\workers-py\api_run.log'
}
# 2) tunnel
Start-Job -ScriptBlock {
  param($cf, $log, $json)
  & $cf tunnel --url http://localhost:8000 --logfile $json --loglevel info *> $log
} -ArgumentList $cf, $log, $tunnelJson

# aguarda backend ficar pronto
$ready = $false
for ($i = 0; $i -lt 12; $i++) {
  try { $r = curl.exe -s --max-time 2 http://127.0.0.1:8000/health; if ($r -match 'ok') { $ready = $true; break } } catch {}
  Start-Sleep -Seconds 1
}
Write-Host "backend ready: $ready"

# aguarda URL do tunnel
$url = $null
for ($i = 0; $i -lt 20; $i++) {
  if (Test-Path $log) {
    $m = Select-String -Path $log -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' | Select-Object -First 1
    if ($m) { $url = $m.Matches[0].Value.Trim(); break }
  }
  Start-Sleep -Seconds 1
}
Write-Host "tunnel url: $url"
if ($url) {
  Set-Content -Path "$root\backend_url.txt" -Value $url
  Start-Sleep -Seconds 2
  Write-Host '--- PUBLIC /health ---'; curl.exe -s --max-time 10 "$url/health"; Write-Host
  Write-Host '--- PUBLIC /v1/version ---'; curl.exe -s --max-time 10 "$url/v1/version"; Write-Host
  Write-Host '--- PUBLIC /v1/events/types ---'; curl.exe -s --max-time 10 "$url/v1/events/types" | Select-String -Pattern '"types"' | Select-Object -First 1; Write-Host
}
