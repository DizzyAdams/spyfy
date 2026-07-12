# Deploy da SpyFy API no Coolify via REST API v1 (https://coolify.io).
#
# Pré-requisitos (Coolify v4):
#   - Instância Coolify rodando (self-hosted ou coolify.dev).
#   - API habilitada (Settings -> API Keys) e um token com ability "deploy".
#   - Recurso "Docker Compose" criado apontando para
#     apps/workers-py/docker-compose.yml (service `spyfy-api`).
#
# Uso:
#   # Deploy direto pelo UUID da aplicação:
#   .\scripts\deploy-coolify.ps1 -CoolifyHost https://seu.coolify.dev `
#       -Token $env:COOLIFY_TOKEN -ApplicationUuid <uuid>
#
#   # Ou resolva o UUID pelo nome (precisa de ability "read" no token):
#   .\scripts\deploy-coolify.ps1 -CoolifyHost https://seu.coolify.dev `
#       -Token $env:COOLIFY_TOKEN -ApplicationName spyfy-api
#
#   # Só valida a descoberta do UUID sem disparar deploy:
#   .\scripts\deploy-coolify.ps1 -CoolifyHost https://seu.coolify.dev `
#       -Token $env:COOLIFY_TOKEN -ApplicationName spyfy-api -DryRun
#
# Notas:
#   - A rota de deploy segue o padrão Coolify v4
#     POST /api/v1/applications/{uuid}/deployments.
#   - Se a sua instância usar rota diferente, passe -DeployEndpoint.
#   - NÃO roda docker localmente; apenas orquestra o deploy na instância.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CoolifyHost,

    [Parameter(Mandatory = $true)]
    [string]$Token,

    # UUID da aplicação no Coolify (opcional se for passar -ApplicationName).
    [string]$ApplicationUuid,

    # Nome da aplicação para resolver o UUID via GET /api/v1/applications.
    [string]$ApplicationName,

    # Força rebuild da imagem mesmo sem mudanças de código.
    [switch]$Force,

    # Rota de deploy (sobrescreve o padrão v4 se necessário).
    [string]$DeployEndpoint = '/api/v1/applications/{uuid}/deployments',

    # Apenas descobre o UUID e valida a conexão; não dispara deploy.
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# Normaliza o host (remove barra final) e monta a base da API.
$host_ = $CoolifyHost.Trim()
if ($host_.EndsWith('/')) { $host_ = $host_.Substring(0, $host_.Length - 1) }
$base = if ($host_ -match '^https?://') { $host_ } else { "https://$host_" }
$base = $base.TrimEnd('/')

$headers = @{
    'Authorization' = "Bearer $Token"
    'Accept'        = 'application/json'
}

function Invoke-Coolify($method, $path, $body) {
    $url = "$base$path"
    $splat = @{ Method = $method; Uri = $url; Headers = $headers; ErrorAction = 'Stop' }
    if ($body) {
        $splat['ContentType'] = 'application/json'
        $splat['Body'] = ($body | ConvertTo-Json -Compress -Depth 6)
    }
    try {
        $resp = Invoke-RestMethod @splat
        return @{ Status = 200; Body = $resp }
    }
    catch [System.Net.WebException] {
        $we = $_.Exception
        $code = [int]$we.Response.StatusCode
        $detail = ''
        try { $detail = (New-Object System.IO.StreamReader($we.Response.GetResponseStream())).ReadToEnd() } catch {}
        return @{ Status = $code; Body = $detail }
    }
}

Write-Host "[Coolify] Host: $base"

# Healthcheck da API do Coolify.
$health = Invoke-Coolify 'GET' '/api/v1/health'
if ($health.Status -ne 200) {
    Write-Error "[Coolify] API indisponivel (HTTP $($health.Status)). Verifique host/token. Resposta: $($health.Body)"
    exit 1
}
Write-Host '[Coolify] API ok (health 200).'

# Resolve o UUID da aplicação.
if (-not $ApplicationUuid) {
    if (-not $ApplicationName) {
        Write-Error '[Coolify] Informe -ApplicationUuid OU -ApplicationName.'
        exit 1
    }
    $list = Invoke-Coolify 'GET' '/api/v1/applications'
    if ($list.Status -ne 200) {
        Write-Error "[Coolify] Falha ao listar aplicacoes (HTTP $($list.Status)): $($list.Body)"
        exit 1
    }
    $apps = $list.Body
    if ($apps -is [PSObject] -and $apps.PSObject.Properties['data']) { $apps = $apps.data }
    $match = @($apps) | Where-Object { $_.name -eq $ApplicationName -or $_.uuid -eq $ApplicationName } | Select-Object -First 1
    if (-not $match) {
        Write-Error "[Coolify] Aplicacao '$ApplicationName' nao encontrada. Apps disponiveis: $((@($apps).name -join ', '))"
        exit 1
    }
    $ApplicationUuid = $match.uuid
    Write-Host "[Coolify] App '$($match.name)' -> uuid=$ApplicationUuid"
}

if ($DryRun) {
    Write-Host "[Coolify] DryRun: deploy NAO disparado para $ApplicationUuid."
    exit 0
}

# Dispara o deploy.
$endpoint = $DeployEndpoint.Replace('{uuid}', $ApplicationUuid)
$deployBody = @{ force = [bool]$Force }
$result = Invoke-Coolify 'POST' $endpoint $deployBody

if ($result.Status -ge 200 -and $result.Status -lt 300) {
    Write-Host "[Coolify] Deploy disparado com sucesso (HTTP $($result.Status))."
    $result.Body | ConvertTo-Json -Depth 6 | Write-Host
    Write-Host '[Coolify] Acompanhe o log em: painel do Coolify -> aplicacao -> Deployments.'
}
else {
    Write-Error "[Coolify] Falha ao disparar deploy (HTTP $($result.Status)): $($result.Body)"
    exit 1
}
