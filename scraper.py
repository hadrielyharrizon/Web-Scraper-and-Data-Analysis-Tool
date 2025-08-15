import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import os
import datetime
import matplotlib.pyplot as plt

URL = 'https://lista.mercadolivre.com.br/celular'
CATEGORIA = 'celular'
PASTA_DATA = 'data'
os.makedirs(PASTA_DATA, exist_ok=True)
DATA_HORA = datetime.datetime.now().strftime('%Y%m%S')


def limpar_texto(texto):
    if texto:
        return texto.replace('\u202f'," ").replace('�', '').strip()
    return None


def save_data_txt(data, filename):
    """Salva dados brutos em arquivo TXT."""
    path = os.path.join(PASTA_DATA, filename)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(f'{item}\n')
        print(f'Dados salvos em TXT: {path}')


def save_data_csv(produtos, filename):
    """Salva dados brutos em CSV."""
    df = pd.DataFrame(produtos)
    path = os.path.join(PASTA_DATA,filename)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    print(f'Dados salvos em CSV: {path}')
    return path


def save_data_sqlite(produtos, db_name='produtos.db'):
    """Salva dados em SQLite na raix do projeto."""
    db_path = os.path.abspath(db_name)
    conn = sqlite3.connect(db_path)
    df = pd.DataFrame(produtos)
    df.to_sql('produtos', conn, if_exists='append', index=False)
    total = conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]
    conn.close()
    print(f"Dados salvos em SQLite: {db_path} (linhas na tabela 'produtos': {total})")

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

    itens = soup.select('li.ui-search-layout__item') or soup.select('div.ui-search-result__wrapper')
    print(f'Quantidade de itens encontrados: {len(itens)}')

    for item in itens:
 
        try:
            nome_tag = item.select_one('h2.ui-search-item__title') or item.select_one('a.poly-component__title') or item.select_one('.ui-search-item__title')
            nome = limpar_texto(nome_tag.get_text()) if nome_tag else 'Sem nome'

            preco = 0.0

            preco_inteiro_tag = item.select_one('span.andes-money-amount__fraction') or item.select_one('span.price-tag-fraction')
            preco_centavos_tag = item.select_one('span.andes-money-amount__cents') or item.select_one('span.price-tag-cents')
            

            if preco_inteiro_tag:
                preco_text = preco_inteiro_tag.get_text(strip=True).replace(".", "").replace(",", ".")
                preco = float(preco_text)
                
                if preco_centavos_tag:
                    centavos_text = preco_centavos_tag.get_text(strip=True).zfill(2)       
                    preco += float('0.' + centavos_text)
                    
                    

            aval_tag = item.select_one("span.ui-search-reviews__rating-number")
            avaliacao = float(aval_tag.get_text(strip=True).replace(',','.')) if aval_tag else None 
            

            produtos.append({
                "nome": nome,
                "preco": preco,
                "avaliacao": avaliacao,
                "categoria": termo_busca
            })
        except Exception:
            continue

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_data_txt([str(p) for p in produtos], f'mercado_livre_{timestamp}.txt')
    save_data_csv(produtos, f'mercado_livre_{timestamp}.csv')
    save_data_sqlite(produtos)

    return produtos

def coletar_produtos():
    return scrape_mercado_livre("celular")

def analisar_produtos(produtos):
    """Realiza análise rápida de preços e avaliações."""
    if not produtos:
        print("Nenhum produto para analisar.")
        return
    precos = [p['preco'] for p in produtos if p['preco'] is not None]
    avaliacoes = [p['avaliacao'] for p in produtos if p ['avaliacao'] is not None]

    print('\n---Análise rápida---')
    print(f'Quantidade de produtos: {len(produtos)}')
    print(f'Preço médio: R$ {sum(precos)/len(precos):.2f}')
    print(f'Produto mais barato: R$ {min(precos):.2f}')
    print(f'Produto mais caro: R$ {max(precos):.2f}')

    if avaliacoes:
        print(f'Avaliação média: {sum(avaliacoes)/len(avaliacoes):.2f}')
    else:
        print('Não há avaliações disponíveis.')

    #Grafico
    plt.figure(figsize=(10,5))
    plt.hist(precos, bins=10, color='skyblue', edgecolor='black')
    plt.title('Distribuição de preços')
    plt.xlabel('Preço (R$)')
    plt.ylabel('Quantidade de produtos')
    plt.show()

if __name__ == "__main__":
    produtos = coletar_produtos()
    for produto in produtos:
        print(produto)
    
    print('\nVerificação rápida dos preços: ')
    for produto in produtos[:10]:
        nome = produto['nome'].replace('\u202f', ' ')
        preco = produto['preco']
        print(f'{nome} - R$ {preco:.2f}')

    analisar_produtos(produtos)
    