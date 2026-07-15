"""Gera cache/cookies.json a partir de um login manual no Facebook.

Uso (rode uma vez, com display):
    python apps/workers-py/generate_fb_cookies.py

Abre o Facebook, você faz login manualmente, aguarda ~15s (ou feche a janela),
e o script salva os cookies em cache/cookies.json no formato que o
browser_scraper.scrape_native_ads_session consome (lista de {name,value}).

Depois disso, `python -m spyfy.scraper_bridge --network meta` raspa a Meta Ad
Library REAL (sem login wall) usando esses cookies. Nada é enviado a lugar
nenhum além do seu próprio disco local.
"""
import os
import sys
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
OUT = os.path.join(CACHE_DIR, "cookies.json")


def main():
    from playwright.sync_api import sync_playwright

    os.makedirs(CACHE_DIR, exist_ok=True)
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False,
                                 args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = browser.new_context(
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
        locale="pt-BR",
    )
    page = ctx.new_page()
    page.goto("https://www.facebook.com/", wait_until="domcontentloaded", timeout=60000)
    print("\n>>> FAÇA LOGIN NO FACEBOOK NA JANELA QUE ABRIU.")
    print(">>> Após logar, aguarde ~10s ou feche esta janela para salvar.\n")
    try:
        page.wait_for_event("close", timeout=300000)
    except Exception:
        # fallback: aguarda tempo fixo
        time.sleep(20)
    try:
        cookies = ctx.cookies()
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        n = len(cookies)
        has_session = any(c["name"] in ("c_user", "datr", "xs") for c in cookies)
        print(f"[ok] {n} cookies salvos em {OUT}")
        print(f"[ok] sessão válida (c_user/xs): {has_session}")
        if not has_session:
            print("[aviso] não detectei cookie de sessão (c_user/xs) — "
                  "o login pode não ter completado. Tente de novo.")
    except Exception as e:
        print("[erro] ao salvar cookies:", e)
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
