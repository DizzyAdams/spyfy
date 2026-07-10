# 🌐 Proxy Pool — Guia (Loop 7)

Como usar o `ProxyPool` para **driblar Cloudflare / rate-limit** nos scrapers (Meta Ad Library, TikTok, etc.). Código: `spyfy/proxy_pool.py` (testes ✅).

## Por que sticky import
O Cloudflare **prende o desafio à sessão/IP**. Se você troca de proxy no meio do desafio, ele falha. `Rotation.STICKY` + `sticky_id` mantém o **mesmo proxy** durante toda a sessão de um alvo → clearance estável.

```python
pool = ProxyPool(proxies, rotation=Rotation.STICKY)
p = pool.get(region="BR", sticky_id="meta-keto-ana")
# usa p.url em TODAS as requisições dessa sessão
```

## Residenciais > Datacenter p/ Cloudflare
- `ProxyType.RESIDENTIAL` / `MOBILE`: passam no CF na maioria.
- `DATACENTER`: barrados com frequência (use só p/ alvos sem CF).

## Health check & auto-ban
```python
t0 = time.time()
ok = requests.get(url, proxies={"http": p.url}, timeout=10).ok
pool.report(p, ok=ok, latency_ms=(time.time()-t0)*1000)
# 3 falhas => p.banned => sai do pool
```
`pool.stats()` → `{total, banned, available}`.

## Rotação ponderada
`ROUND_ROBIN` escolhe o proxy de **maior score** (taxa de sucesso − penalidade de latência). `RANDOM` para anonimato máximo.

## Scraper wrapper (exemplo)
```python
import httpx
def fetch(url, pool, sticky_id, region="BR"):
    p = pool.get(region=region, sticky_id=sticky_id)
    client = httpx.Client(proxies={"all": p.url},
                          headers={"User-Agent": UA, "Accept-Language": "pt-BR"})
    r = client.get(url, follow_redirects=True)
    pool.report(p, ok=r.status_code == 200,
                latency_ms=r.elapsed.total_seconds()*1000)
    return r
```

## Boas práticas anti-CF
- Headers de browser real (UA, sec-ch-ua, accept-language).
- `cf_clearance` cookie persistido por sessão sticky.
- Backoff exponencial em 403/Challenge.
- Misturar regiões (BR/US) conforme o alvo.

## Testado
`test_proxies_crm_cart.py`: sticky mantém sessão; ban após 3 falhas; filtro por região.
