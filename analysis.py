import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import plotly.express as px
import os

DB_PATH = os.path.join(os.getcwd(), 'produtos.db')

# Conectar ao SQLite e ler dados
print(f"Lendo dados de: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query('SELECT * FROM produtos', conn)
conn.close()

print(f"Linhas carregadas: {len(df)}\n")
print("Amostra (últimas 5 linhas):")
print(df.tail())

# Resumo de preços
precos = df['preco'].dropna()
print("\nResumo de preços:")
print(f"  média: R$ {precos.mean():.2f}")
print(f"  min:   R$ {precos.min():.2f}")
print(f"  max:   R$ {precos.max():.2f}")

# ---------------------------
# 1️⃣ Histograma de preços (Matplotlib)
plt.figure(figsize=(10,5))
plt.hist(precos, bins=15, color='skyblue', edgecolor='black')
plt.title('Distribuição de preços dos produtos')
plt.xlabel('Preço (R$)')
plt.ylabel('Quantidade de produtos')
plt.grid(axis='y', alpha=0.75)
plt.show()

# ---------------------------
# 2️⃣ Top 10 produtos mais caros (Bar chart)
top10 = df.nlargest(10, 'preco')
plt.figure(figsize=(12,6))
plt.barh(top10['nome'], top10['preco'], color='salmon')
plt.xlabel('Preço (R$)')
plt.title('Top 10 produtos mais caros')
plt.gca().invert_yaxis()  # Inverte o eixo para melhor visualização
plt.show()

# ---------------------------
# 3️⃣ Quantidade de produtos por categoria (Matplotlib)
cat_counts = df['categoria'].value_counts()
plt.figure(figsize=(6,4))
plt.bar(cat_counts.index, cat_counts.values, color='lightgreen')
plt.title('Quantidade de produtos por categoria')
plt.ylabel('Quantidade')
plt.show()

# ---------------------------
# 4️⃣ Gráfico interativo de preços (Plotly)
fig = px.histogram(df, x='preco', nbins=20, color='categoria',
                   title='Distribuição de preços (interativo)',
                   labels={'preco':'Preço (R$)', 'categoria':'Categoria'})
fig.show()

# ---------------------------
# 5️⃣ Scatter interativo: Preço x Avaliação
# Só produtos com avaliação
df_avaliados = df.dropna(subset=['avaliacao'])
if not df_avaliados.empty:
    fig2 = px.scatter(df_avaliados, x='avaliacao', y='preco', color='categoria',
                      hover_data=['nome'], title='Preço x Avaliação (interativo)')
    fig2.show()
else:
    print("\nNão há avaliações para gerar gráfico interativo de Preço x Avaliação.")
