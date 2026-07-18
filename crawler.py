import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag, urlparse
import csv
import time
from collections import deque

def crawler_definitivo(seed_url):
    print(f"Iniciando a Colheitadeira em MODO INFINITO: {seed_url}")
    
    # 1. A Trava de Segurança: Extrai o domínio base (ex: camillodantas.com.br)
    # Isso impede que o robô escape para o YouTube, LinkedIn, etc.
    dominio_alvo = urlparse(seed_url).netloc
    
    # 2. Arquitetura de Fila Rápida: 'deque' não trava a memória com milhares de itens
    urls_to_visit = deque([seed_url])
    visited_urls = set()
    catalog = set()

    # O disfarce anti-bloqueio
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })

    paginas_rastreadas = 0

    # 3. O Laço Infinito: Roda enquanto houver links na fila
    while urls_to_visit:
        # Puxa o próximo link da fila
        current_url = urls_to_visit.popleft() 
        current_url, _ = urldefrag(current_url)

        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)
        paginas_rastreadas += 1
        print(f"[{paginas_rastreadas}] Rastreando: {current_url}")

        try:
            response = scraper.get(current_url, timeout=45)
            
            # Filtro de Sanidade: Só lê a página se for HTML (ignora PDFs e Imagens pesadas)
            if 'text/html' not in response.headers.get('Content-Type', ''):
                continue

            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                full_url, _ = urldefrag(full_url)
                
                if full_url.startswith('http'):
                    # Salva no catálogo (o 'set' já impede duplicação)
                    catalog.add((current_url, full_url))
                    
                    # A REGRA DE OURO DA RASPAGEM INFINITA:
                    # Só enfileira a página para visitar SE for do mesmo domínio alvo
                    if urlparse(full_url).netloc == dominio_alvo:
                        if full_url not in visited_urls and full_url not in urls_to_visit:
                            urls_to_visit.append(full_url)
                            
            # Pausa de 1 segundo (Respeito ao servidor e evita banimento de IP)
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro ao acessar {current_url}: {e}")

    # Exportação Final
    print(f"\n=======================================================")
    print(f"Fim da Linha! O site inteiro foi mapeado.")
    print(f"Salvando {len(catalog)} links ÚNICOS no arquivo CSV...")
    
    with open('catalogo_links.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['origem', 'link_encontrado'])
        for origem, destino in catalog:
            writer.writerow([origem, destino])

if __name__ == "__main__":
    # URL Alvo Principal
    URL_ALVO = "https://materiaisgratuitos.net.br/dicionrio-do-mercado-imobilirio"
    
    # Inicia o Cronômetro
    tempo_inicio = time.time() 
    
    # Dispara a função sem limite de páginas
    crawler_definitivo(URL_ALVO)
    
    # Finaliza o Cronômetro
    tempo_fim = time.time()
    
    print(f"⏱️ Missão Cumprida: Tempo total de execução: {(tempo_fim - tempo_inicio):.2f} segundos.")
    print(f"=======================================================\n")
