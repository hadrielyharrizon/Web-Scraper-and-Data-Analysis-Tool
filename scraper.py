import requests
from bs4 import BeautifulSoup

def scrape_mercado_livre(termo_busca):
    termo_url = termo_busca.strip().replace('', '-')
    url = f'https://lista.mercadolivre.com.br/{termo_url}'
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f'[scraper] Erro ao acessar {url}: {e}')
        return []


    soup = BeautifulSoup(resp.text, 'html.parser')

    produtos = []
    itens = soup.select('li.ui-search-layout__item')
    if not itens:
        itens = soup.select('div.ui-search-result__wrapper')

    for item in itens:
        try:
            nome_tag = item.select_one('h2.ui-search-item__title') or item.select_one('.ui-search-item__title')
            nome = nome_tag.get_text(strip=True) if nome_tag else 'Sem nome'

            preco_tag = item.select_one('span.price-tag-fraction')
            centavos_tag = item.select_one('span.price-tag-cents')
            preco = 0.0
            if preco_tag:
                preco_text = preco_tag.get_text(strip=True).replace(".", "").replace(",", ".")
                preco = float(preco_text)
                if centavos_tag:
                    cents_text = centavos_tag.get_text(strip=True)
                        
                    cents_text = cents_text.zfill(2)
                    preco += float("0." + cents_text)     

            aval_tag = item.select_one("span.ui-search-reviews__rating-number")
            avaliacao = None
            if aval_tag:
                try:
                    avaliacao = float(aval_tag.get_text(strip=True).replace(",", "."))
                except ValueError:
                    avaliacao = None

            produtos.append({
                "nome": nome,
                "preco": preco,
                "avaliacao": avaliacao,
                "categoria": termo_busca
            })
        except Exception:
            # se um item quebrar, ignora e segue
            continue

    return produtos