# SpyFy — sobe web + API + proxy basic auth + tunel cloudflared e captura a URL.
# Sem Docker (daemon bloqueado neste sandbox). Uso: powershell -File scripts/tunnel.ps1
$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$env:NEXT_TELEMETRY_DISABLED = '1'

# garante web (:3000) no ar
try { (Invoke-WebRequest http://localhost:3000 -UseBasicParsing -TimeoutSec 3).StatusCode | Out-Null }
catch {
    Start-Process -NoNewWindow -FilePath "$root\apps\web\node_modules\.bin\next" `
        -ArgumentList 'start', '-p', '3000' `
        -RedirectStandardOutput "$root\web.log" -RedirectStandardError "$root\web.err"
    Start-Sleep -Seconds 5
}

# senha forte + proxy basic auth (:8080 -> :3000)
$pw = (python -c "import secrets;print(secrets.token_urlsafe(12))")
$pw | Out-File "$root\.tunnel_ps.txt" -NoNewline
$env:BASIC_AUTH_USER = 'spyfy'
$env:BASIC_AUTH_PASSWORD = $pw
Start-Process -NoNewWindow -FilePath 'python' `
    -ArgumentList "$root\scripts\basic_auth_proxy.py" `
    -RedirectStandardOutput "$root\proxy.log" -RedirectStandardError "$root\proxy.err"
Start-Sleep -Seconds 3

# tunel cloudflared -> proxy:8080
Remove-Item "$root\cf.log" -ErrorAction SilentlyContinue
Start-Process -NoNewWindow -FilePath 'cloudflared' `
    -ArgumentList 'tunnel', '--url', 'http://localhost:8080' `
    -RedirectStandardOutput "$root\cf.log" -RedirectStandardError "$root\cf.err"

$url = ''
for ($i = 0; $i -lt 22; $i++) {
    Start-Sleep -Seconds 1
    $c = Get-Content "$root\cf.log" -ErrorAction SilentlyContinue
    if ($c) {
        $m = $c | Select-String -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' | Select-Object -First 1
        if ($m) { $url = $m.Matches.Value; break }
    }
}

$info = "URL=$url`nUSER=spyfy`nPASS=$pw"
$info | Out-File "$root\.tunnel_info.txt"
Write-Output $info
