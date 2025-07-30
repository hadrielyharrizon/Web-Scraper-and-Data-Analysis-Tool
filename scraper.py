import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://lista.mercadolivre.com.br/notebook'

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

products = []

for item in soup.select('.ui-search-result__content-wrapper'):
    name = item.select_one('.ui-search-item__title')
    price = item.select_one('.price-tag-fraction')
    link = item.select_one('a.ui-search-link')

    products.append({
        'name': name.text if name else '',
        'price': price.text if price else '',
        'link': link['href'] if link else ''
    })

    df = pd.DataFrame(products)

    df.to_csv('data/products.csv', index=False, encoding='utf-8-sig')
    print('Dados salvos em data/products.csv')