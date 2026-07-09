import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
import csv
import time

def crawler_mvp(seed_url, max_pages=5):
    print(f"Iniciando a colheitadeira furtiva em: {seed_url}")
    visited_urls = set()
    urls_to_visit = [seed_url]
    
    # MUDANÇA DE ARQUITETURA: Trocamos a lista [] por um Set ()
    # O Set automaticamente deleta qualquer linha duplicada!
    catalog = set()

    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })

    while urls_to_visit and len(visited_urls) < max_pages:
        current_url = urls_to_visit.pop(0)
        
        # Limpa qualquer "lixo" (fragmentos #) da URL que estamos visitando agora
        current_url, _ = urldefrag(current_url)

        if current_url in visited_urls:
            continue

        print(f"Rastreando: {current_url}")
        visited_urls.add(current_url)

        try:
            response = scraper.get(current_url, timeout=45)
            
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(current_url, href)
                
                # A MAGIA DA LIMPEZA: Corta fora as âncoras (#advisory, #contato)
                full_url, _ = urldefrag(full_url)
                
                if full_url.startswith('http'):
                    # Salva como uma tupla dentro do Set. Se já existir, o Python ignora.
                    catalog.add((current_url, full_url))
                    
                    if seed_url in full_url and full_url not in visited_urls and full_url not in urls_to_visit:
                        urls_to_visit.append(full_url)
                        
            time.sleep(2)
            
        except Exception as e:
            print(f"Erro ao acessar {current_url}: {e}")

    # Exportação dos dados limpos
    print(f"\nFinalizado! Salvando {len(catalog)} links ÚNICOS no arquivo CSV...")
    with open('catalogo_links.csv', 'w', newline='', encoding='utf-8') as f:
        # Mudamos de DictWriter para writer comum, pois agora lidamos com tuplas
        writer = csv.writer(f)
        writer.writerow(['origem', 'link_encontrado'])
        for origem, destino in catalog:
            writer.writerow([origem, destino])

if __name__ == "__main__":
    URL_ALVO = "https://camillodantas.com.br/"
    LIMITE_PAGINAS = 10 
    
    # LIGA O CRONÔMETRO
    tempo_inicio = time.time() 
    
    # Roda a colheitadeira
    crawler_mvp(URL_ALVO, max_pages=LIMITE_PAGINAS)
    
    # DESLIGA O CRONÔMETRO E CALCULA O RESULTADO
    tempo_fim = time.time()
    tempo_total = tempo_fim - tempo_inicio
    
    print(f"\n⏱️ Relatório de Telemetria:")
    print(f"A colheita levou um total de {tempo_total:.2f} segundos para ser concluída.")
