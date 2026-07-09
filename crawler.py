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

    # Configuração de cabeçalhos para simular um navegador real (Evita Bloqueios/403)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive'
    }

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        
        if current_url in visited_urls:
            continue

        print(f"Rastreando: {current_url}")
        visited_urls.add(current_url)

        try:
            # Faz a requisição HTTP disfarçado de usuário comum
            response = requests.get(current_url, headers=headers, timeout=10)
            
            # Log crucial para auditoria no painel do GitHub Actions
            print(f"Resposta do servidor: Status {response.status_code}")
            
            if response.status_code != 200:
                print(f"Aviso: Página pulada devido ao status de erro {response.status_code}")
                continue
            
            # Faz o parse do HTML da página
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Encontra todas as tags de âncora <a>
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Converte links relativos em absolutos
                full_url = urljoin(current_url, href)
                
                if full_url.startswith('http'):
                    catalog.append({
                        'origem': current_url,
                        'link_encontrado': full_url
                    })
                    
                    # Restrição de escopo: o robô só enfileira páginas do mesmo domínio do site alvo
                    if seed_url in full_url and full_url not in visited_urls:
                        urls_to_visit.append(full_url)
                        
            # Boas práticas: 1 segundo de intervalo para respeitar o servidor alvo
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro ao acessar {current_url}: {e}")

    # Salva os dados coletados no arquivo CSV
    print(f"\nFinalizado! Salvando {len(catalog)} links no arquivo CSV...")
    with open('catalogo_links.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['origem', 'link_encontrado'])
        writer.writeheader()
        writer.writerows(catalog)

if __name__ == "__main__":
    # =========================================================================
    # CONFIGURAÇÃO DO ALVO: Altere os valores abaixo para rodar o projeto
    # =========================================================================
    
    # 1. Coloque a URL do site que deseja rastrear entre as aspas:
    URL_ALVO = "https://camillodantas.com.br/"
    
    # 2. Defina o limite máximo de páginas internas que o robô irá visitar:
    LIMITE_PAGINAS = 5
    
    # Executa a colheita
    crawler_mvp(URL_ALVO, max_pages=LIMITE_PAGINAS)
