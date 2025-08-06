import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os

def scrape_mercado_livre(query, pages=1):
    # Instala o chromedriver compatível automaticamente
    chromedriver_autoinstaller.install()

    options = Options()
    options.add_argument('--headless')  # roda sem abrir janela do navegador
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.binary_location = "/usr/bin/chromium"  # caminho do Chromium no Codespaces

    driver = webdriver.Chrome(options=options)

    results = []

    for page in range(pages):
        # Monta a url da página de busca Mercado Livre
        url = f"https://lista.mercadolivre.com.br/{query}_Desde_{page*50 + 1}"
        print(f"Acessando página: {url}")
        driver.get(url)
        time.sleep(2)  # espera a página carregar

        products = driver.find_elements(By.CSS_SELECTOR, 'li.ui-search-layout__item')

        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, 'h2.ui-search-item__title').text
                price = product.find_element(By.CSS_SELECTOR, 'span.price-tag-fraction').text
                link = product.find_element(By.CSS_SELECTOR, 'a.ui-search-link').get_attribute('href')

                results.append({
                    'Título': title,
                    'Preço (R$)': price,
                    'Link': link
                })
            except Exception:
                continue

    driver.quit()

    # Cria pasta para salvar se não existir
    os.makedirs('data/raw', exist_ok=True)

    if results:
        df = pd.DataFrame(results)
        df.to_csv('data/raw/mercado_livre_resultados.csv', index=False, encoding='utf-8-sig')
        print(f"{len(results)} produtos salvos em 'data/raw/mercado_livre_resultados.csv'")
    else:
        print("Nenhum produto encontrado.")

if __name__ == "__main__":
    scrape_mercado_livre("tenis feminino", pages=2)
