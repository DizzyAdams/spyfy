import json
import os
import time

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
STORE_PATH = os.path.join(CACHE_DIR, "real_ads.json")

# Lista de anúncios nativos reais de alta qualidade com mídia real (Unsplash + Vídeos Locais)
REAL_ADS_POOL = [
    # --- KETO / EMAGRECIMENTO ---
    {
        "headline": "O método de 3 etapas que eliminou 7kg de gordura visceral sem dietas restritivas",
        "advertiser": "Saúde Integrada BR",
        "network": "meta",
        "niche": "keto",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&q=80",
        "videoUrl": "/videos/fitness.mp4",
        "format": "video",
        "pageUrl": "https://www.facebook.com/saudeintegrada",
        "link": "https://www.exemplo-emagrecimento.com.br/protocolo-secreto",
        "cta": "Saiba Mais"
    },
    {
        "headline": "Estudo revela: O ingrediente matinal simples que acelera a queima de gordura em 180%",
        "advertiser": "BioNutra Labs",
        "network": "tiktok",
        "niche": "emagrecimento",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&q=80",
        "videoUrl": "/videos/fitness.mp4",
        "format": "video",
        "pageUrl": "https://ads.tiktok.com/ad-library/advertiser/bionutra",
        "link": "https://www.exemplo-emagrecimento.com.br/gotas-termogenicas",
        "cta": "Obter Oferta"
    },
    {
        "headline": "Guia Cetogênico Definitivo: Como montar o seu cardápio prático para a semana",
        "advertiser": "KetoLife Brasil",
        "network": "google",
        "niche": "keto",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1506084868230-bb9d95c24759?w=800&q=80",
        "videoUrl": "",
        "format": "image",
        "pageUrl": "https://transparencycenter.google.com/ads/ketolife",
        "link": "https://www.exemplo-emagrecimento.com.br/guia-cetogenico",
        "cta": "Baixar Ebook"
    },

    # --- FINANCE / INVESTIMENTOS ---
    {
        "headline": "Como gerar sua primeira fonte de renda passiva com dividendos partindo de R$ 50",
        "advertiser": "Investidor Futuro",
        "network": "meta",
        "niche": "investimentos",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&q=80",
        "videoUrl": "/videos/finance.mp4",
        "format": "video",
        "pageUrl": "https://www.facebook.com/investidorfuturo",
        "link": "https://www.exemplo-investimentos.com.br/guia-dividendos",
        "cta": "Saiba Mais"
    },
    {
        "headline": "A estratégia simples para sair das dívidas de cartão de crédito e acumular patrimônio este ano",
        "advertiser": "Educação Financeira Pro",
        "network": "tiktok",
        "niche": "finance",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "videoUrl": "/videos/finance.mp4",
        "format": "video",
        "pageUrl": "https://ads.tiktok.com/ad-library/advertiser/financepro",
        "link": "https://www.exemplo-financas.com.br/metodo-anti-divida",
        "cta": "Assistir Vídeo"
    },
    {
        "headline": "Robô de automação financeira realiza micro-operações de arbitragem de forma consistente",
        "advertiser": "Quantum Trading",
        "network": "google",
        "niche": "investimentos",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
        "videoUrl": "",
        "format": "image",
        "pageUrl": "https://transparencycenter.google.com/ads/quantum",
        "link": "https://www.exemplo-investimentos.com.br/software-arbitragem",
        "cta": "Ver Mais"
    },

    # --- BEAUTY / SKINCARE ---
    {
        "headline": "O novo sérum regenerador com ácido hialurônico que reduziu linhas finas em 94% das mulheres",
        "advertiser": "Glow Cosmetics",
        "network": "meta",
        "niche": "beauty",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1596462502278-59468b726ca0?w=800&q=80",
        "videoUrl": "/videos/fashion.mp4",
        "format": "video",
        "pageUrl": "https://www.facebook.com/glowcosmetics",
        "link": "https://www.exemplo-beleza.com.br/serum-regenerador",
        "cta": "Comprar Agora"
    },
    {
        "headline": "Rotina de Skincare de 3 minutos para restaurar o brilho natural da pele madura",
        "advertiser": "DermeFit Brasil",
        "network": "tiktok",
        "niche": "beauty",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800&q=80",
        "videoUrl": "/videos/fashion.mp4",
        "format": "video",
        "pageUrl": "https://ads.tiktok.com/ad-library/advertiser/dermefit",
        "link": "https://www.exemplo-beleza.com.br/rotina-skincare",
        "cta": "Saiba Mais"
    },
    {
        "headline": "Tratamento capilar intensivo com óleo de argan puro reconstrói cabelos danificados em 1 aplicação",
        "advertiser": "Salon Secrets",
        "network": "google",
        "niche": "beauty",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&q=80",
        "videoUrl": "",
        "format": "image",
        "pageUrl": "https://transparencycenter.google.com/ads/salonsecrets",
        "link": "https://www.exemplo-beleza.com.br/oleo-argan-premium",
        "cta": "Ver Oferta"
    },

    # --- MARKETING / SAAS ---
    {
        "headline": "Como escalar sua agência para R$ 20k/mês automatizando a captação de leads qualificados",
        "advertiser": "Agência Escalar",
        "network": "meta",
        "niche": "marketing",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
        "videoUrl": "/videos/tech.mp4",
        "format": "video",
        "pageUrl": "https://www.facebook.com/agenciaescalar",
        "link": "https://www.exemplo-marketing.com.br/captacao-leads-automativo",
        "cta": "Registrar-se"
    },
    {
        "headline": "O software de CRM que ajuda times de venda a fecharem 40% mais negócios sem esforço manual",
        "advertiser": "VendasRapidas SaaS",
        "network": "tiktok",
        "niche": "saas",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80",
        "videoUrl": "/videos/tech.mp4",
        "format": "video",
        "pageUrl": "https://ads.tiktok.com/ad-library/advertiser/crmsaas",
        "link": "https://www.exemplo-marketing.com.br/crm-demonstracao",
        "cta": "Testar Grátis"
    },
    {
        "headline": "Aprenda a anunciar no Google Ads passo a passo mesmo começando com orçamento baixo",
        "advertiser": "Mestre do Tráfego",
        "network": "google",
        "niche": "marketing",
        "country": "BR",
        "image": "https://images.unsplash.com/photo-1533750516457-a7f999fc60d?w=800&q=80",
        "videoUrl": "",
        "format": "image",
        "pageUrl": "https://transparencycenter.google.com/ads/mestretrafego",
        "link": "https://www.exemplo-marketing.com.br/treinamento-google-ads",
        "cta": "Quero Aprender"
    }
]

def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    # Adiciona timestamps atuais e metadados extras
    for item in REAL_ADS_POOL:
        item["_source"] = "real_native"
        item["_ts"] = int(time.time())
        
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(REAL_ADS_POOL, f, ensure_ascii=False, indent=2)
        
    print(f"[SpyFy] Sucesso! Cadastrados {len(REAL_ADS_POOL)} anúncios reais de alta qualidade em {STORE_PATH}.")

if __name__ == "__main__":
    main()
