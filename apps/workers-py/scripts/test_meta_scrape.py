import os
import sys

# Adicionar diretório pai ao path antes de importar spyfy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spyfy.meta_library import MetaAdLibrary

def main():
    token = os.getenv("META_ACCESS_TOKEN", "")
    print(f"Iniciando teste de busca da Meta Ad Library...")
    print(f"Token configurado no ambiente: {'Sim (tamanho ' + str(len(token)) + ')' if token else 'Não'}")
    
    client = MetaAdLibrary(access_token=token, country="BR")
    try:
        results = client.search(query="keto", limit=3)
        print(f"\nBusca concluída! Resultados encontrados: {len(results)}")
        for idx, offer in enumerate(results):
            print(f"\n--- Resultado {idx + 1} ---")
            print(f"ID: {offer.get('id')}")
            print(f"Anunciante: {offer.get('advertiser')}")
            print(f"Headline: {offer.get('headline')}")
            print(f"Link do Criativo: {offer.get('image') or offer.get('videoUrl')}")
            print(f"Link da Oferta (CTA): {offer.get('link')}")
    except Exception as e:
        print(f"\nErro ao buscar da Meta Ad Library: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
