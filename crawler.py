import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import time

def crawler_mvp(seed_url, max_pages=5):
    print(f"Iniciando o crawler em: {seed_url}")
    visited_urls = set()
    urls_to_visit = [seed_url]
    catalog = []

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue

        print(f"Rastreando: {current_url}")
        visited_urls.add(current_url)

        try:
            # Faz a requisição HTTP
            response = requests.get(current_url, timeout=5)
            # Ignora se a página não carregar com sucesso (código 200)
            if response.status_code != 200:
                continue
            
            # Faz o parse do HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontra todas as tags de âncora <a>
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Converte links relativos (ex: /sobre) em absolutos (ex: site.com/sobre)
                full_url = urljoin(current_url, href)
                
                # Guarda o link encontrado no nosso catálogo
                if full_url.startswith('http'):
                    catalog.append({
                        'origem': current_url,
                        'link_encontrado': full_url
                    })
                    
                    # Regra de segurança do MVP: só enfileira páginas do mesmo domínio
                    if seed_url in full_url and full_url not in visited_urls:
                        urls_to_visit.append(full_url)
                        
            # Pausa de 1 segundo para sermos educados com o servidor (Boas práticas de Engenharia)
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro ao acessar {current_url}: {e}")

    # Salva os dados em um CSV
    print(f"\nFinalizado! Salvando {len(catalog)} links no arquivo CSV...")
    with open('catalogo_links.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['origem', 'link_encontrado'])
        writer.writeheader()
        writer.writerows(catalog)

if __name__ == "__main__":
    # Usando um site de testes feito especificamente para raspagem
    URL_ALVO = "https://quotes.toscrape.com/"
    crawler_mvp(URL_ALVO, max_pages=5)
