import requests
from bs4 import BeautifulSoup
import os
import datetime


def save_data(data, filename="raw_data.txt"):
    """Salva dados brutos em arquivo."""
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", filename)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f'{item}\n')
        print(f'Dados salvos em {path}')


def scrape_mercado_livre(termo_busca):
    termo_url = termo_busca.strip().replace(' ', '-')
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

    with open('pagina.html', "w", encoding="utf-8") as f:
        f.write(resp.text)
    print('HTML salvo em pagina.html')

    soup = BeautifulSoup(resp.text, 'html.parser')


    produtos = []

    itens = soup.select('li.ui-search-layout__item')
    if not itens:
        itens = soup.select('div.ui-search-result__wrapper')

    print(f'Quantidade de itens encontrados: {len(itens)}')


    for item in itens:
        try:
            nome_tag = item.select_one('h2.ui-search-item__title') or item.select_one('a.poly-component__title') or item.select_one('.ui-search-item__title')
            nome = nome_tag.get_text(strip=True) if nome_tag else 'Sem nome'

            preco_inteiro_tag = item.select_one('span.price-tag-fraction')
            preco_centavos_tag = item.select_one('span.price-tag-cents')
            
            preco = 0.0

            if preco_inteiro_tag:
                preco_text = preco_inteiro_tag.get_text(strip=True).replace(".", "").replace(",", ".")
                try:
                    preco = float(preco_text)
                except:
                    preco = 0.0

                if preco_centavos_tag:
                    centavos_text = preco_centavos_tag.get_text(strip=True).zfill(2)       
                    try:
                        preco += float('0.' + centavos_text)
                    except:
                        pass   

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
            continue

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data([str(p) for p in produtos], f'mercado_livre_{timestamp}.txt')

    return produtos

def coletar_produtos():
    return scrape_mercado_livre("celular")

if __name__ == "__main__":
    produtos = coletar_produtos()
    for produto in produtos:
        print(produto)


    