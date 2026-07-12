$ErrorActionPreference = 'Continue'
$base = 'http://127.0.0.1:8000'

function J($body){ $body | ConvertTo-Json -Compress -Depth 8 }

Write-Host '=== GET /health ==='; curl.exe -s $base/health; Write-Host
Write-Host '=== GET /v1/version ==='; curl.exe -s $base/v1/version; Write-Host
Write-Host '=== GET /v1/events/types ==='; curl.exe -s $base/v1/events/types | Select-String -Pattern 'types' | Select-Object -First 1; Write-Host
Write-Host '=== POST /v1/offers/estimate ==='
curl.exe -s -X POST $base/v1/offers/estimate -H 'Content-Type: application/json' `
  -d (J @{first_seen='2026-01-01T00:00:00'; last_seen='2026-03-01T00:00:00'; creative_variants=5; est_impressions_low=100000; est_impressions_high=500000; engagement=4200; networks=2; countries=1; avg_ticket=97.0; cvr=0.021; ctr=0.014; cpm=7.5}); Write-Host
Write-Host '=== POST /v1/notify ==='
curl.exe -s -X POST $base/v1/notify -H 'Content-Type: application/json' `
  -d (J @{event_id='evt_validation_001'; type='offer.discovered'; plan='pro'; user_id='u_validate'; email='test@spyfy.io'; hour_local=12; sent_today=0; data=@{title='Nova oferta'; body='Oferta vencedora detectada'; priority='normal'} }); Write-Host
Write-Host '=== POST /v1/webhooks/{provider} (sem assinatura -> 401 esperado) ==='
curl.exe -s -o $null -w 'HTTP %{http_code}\n' -X POST $base/v1/webhooks/nexustracker -H 'Content-Type: application/json' -d '{"event_id":"evt_wh_1","type":"offer.discovered","data":{}}'
Write-Host '=== GET /v1/offers?simulate=true ==='
curl.exe -s "$base/v1/offers?simulate=true&limit=3" | Select-String -Pattern 'count' | Select-Object -First 1; Write-Host
Write-Host '=== GET /v1/metrics?simulate=true ==='
curl.exe -s "$base/v1/metrics?simulate=true" | Select-String -Pattern 'winning|roi|top' | Select-Object -First 3; Write-Host
Write-Host '=== GET /v1/offers/{id} ==='
$id = (curl.exe -s "$base/v1/offers?simulate=true&limit=1" | ConvertFrom-Json).offers[0].id
Write-Host "id=$id"
curl.exe -s "$base/v1/offers/$id" | Select-String -Pattern 'id|title|network' | Select-Object -First 3; Write-Host
Write-Host '=== POST /v1/agents/run (simulate, count=1) ==='
$runBody = '{"objective":"Encontrar ofertas vencedoras de saude","niche":"saude","network":"meta","country":"BR","simulate":true,"count":1,"min_score":0.0}'
Set-Content -Path _runbody.json -Value $runBody -NoNewline
curl.exe -s -X POST $base/v1/agents/run -H 'Content-Type: application/json' --data-binary @_runbody.json `
  | Select-String -Pattern 'status|offers|members|error|done_steps' | Select-Object -First 6; Write-Host
Start-Sleep -Seconds 2
Write-Host '=== GET /v1/agents/rag/count (apos run) ==='
curl.exe -s $base/v1/agents/rag/count; Write-Host
Write-Host '=== POST /v1/agents/rag/query ==='
curl.exe -s -X POST $base/v1/agents/rag/query -H 'Content-Type: application/json' `
  -d (J @{text='oferta de saude com alto ROI'; n=3}) | Select-String -Pattern 'count|hits' | Select-Object -First 2; Write-Host
