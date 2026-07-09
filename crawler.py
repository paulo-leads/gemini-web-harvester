import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import time

def crawler_mvp(seed_url, max_pages=5):
    print(f"Iniciando a colheitadeira furtiva em: {seed_url}")
    visited_urls = set()
    urls_to_visit = [seed_url]
    catalog = []

    # Inicializa o scraper projetado para contornar bloqueios (WAF/Cloudflare)
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue

        print(f"Rastreando: {current_url}")
        visited_urls.add(current_url)

        try:
            # Faz a requisição usando o cloudscraper (timeout um pouco maior por causa da evasão)
            response = scraper.get(current_url, timeout=55)
            
            print(f"Resposta do servidor: Status {response.status_code}")
            
            if response.status_code != 200:
                print(f"Aviso: Página pulada devido ao status de erro {response.status_code}")
                continue
            
            # Parse do HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extração dos links
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                
                if full_url.startswith('http'):
                    catalog.append({
                        'origem': current_url,
                        'link_encontrado': full_url
                    })
                    
                    if seed_url in full_url and full_url not in visited_urls:
                        urls_to_visit.append(full_url)
                        
            # Pausa compassiva de 2 segundos para evitar ativar defesas de taxa (Rate Limiting)
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro crítico ao acessar {current_url}: {e}")

    # Exportação dos dados
    print(f"\nFinalizado! Salvando {len(catalog)} links no arquivo CSV...")
    with open('catalogo_links.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['origem', 'link_encontrado'])
        writer.writeheader()
        writer.writerows(catalog)

if __name__ == "__main__":
    # A URL alvo real de vocês
    URL_ALVO = "https://camillodantas.com.br/"
    LIMITE_PAGINAS = 20
    
    crawler_mvp(URL_ALVO, max_pages=LIMITE_PAGINAS)
