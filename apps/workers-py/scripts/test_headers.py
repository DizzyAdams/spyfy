import httpx

URL = "https://www.facebook.com/ads/library/?active_status=ACTIVE&country=BR&q=keto&media_type=all"

# Teste 1: Headers básicos normais
HEADERS_1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# Teste 2: Headers completos imitando Chrome Real
HEADERS_2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
}

def test_headers(name, headers):
    try:
        # Usando HTTP/1.1 explicitamente para ver se ajuda
        with httpx.Client(headers=headers, http2=False, timeout=15.0, follow_redirects=True) as client:
            resp = client.get(URL)
            print(f"[{name}] Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"[{name}] Sucesso! Retornou {len(resp.text)} bytes")
                # Verifica se contém adArchiveId
                if "adArchiveId" in resp.text:
                    print(f"[{name}] Encontrou dados de anúncios no HTML!")
                else:
                    print(f"[{name}] HTML carregado, mas sem dados de anúncio (talvez precise de JS/renderização).")
    except Exception as e:
        print(f"[{name}] Erro: {e}")

print("Iniciando testes de headers...")
test_headers("Básico", HEADERS_1)
test_headers("Chrome Completo", HEADERS_2)
