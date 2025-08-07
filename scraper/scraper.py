import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os

def scrape_mercado_livre(query, pages=1):
    chromedriver_autoinstaller.install()

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(options=options)

    results = []

    for page in range(pages):
        url = f"https://lista.mercadolivre.com.br/{query}_Desde_{page*50 + 1}"
        print(f"Acessando página: {url}")
        driver.get(url)
        time.sleep(3)

        products = driver.find_elements(By.CSS_SELECTOR, 'div.ui-search-result__wrapper')

        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, 'h2.ui-search-item__title').text
                
                # preço dividido em fração e centavos
                price_int = product.find_element(By.CSS_SELECTOR, 'span.price-tag-fraction').text
                price_dec = ''
                try:
                    price_dec = product.find_element(By.CSS_SELECTOR, 'span.price-tag-cents').text
                except:
                    price_dec = '00'
                price = f"{price_int},{price_dec}"

                link = product.find_element(By.CSS_SELECTOR, 'a.ui-search-link').get_attribute('href')

                results.append({
                    'Título': title,
                    'Preço (R$)': price,
                    'Link': link
                })
            except Exception as e:
                # opcional: print(f"Erro ao capturar produto: {e}")
                continue

    driver.quit()

    os.makedirs('data/raw', exist_ok=True)

    if results:
        df = pd.DataFrame(results)
        df.to_csv('data/raw/mercado_livre_resultados.csv', index=False, encoding='utf-8-sig')
        print(f"{len(results)} produtos salvos em 'data/raw/mercado_livre_resultados.csv'")
    else:
        print("Nenhum produto encontrado.")

if __name__ == "__main__":
    scrape_mercado_livre("tenis feminino", pages=2)

