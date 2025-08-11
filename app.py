from flask import Flask, render_template, request, jsonify
from scraper import scrape_mercado_livre
from models import db, Produto
import plotly
import plotly.express as px
import json
import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DB_DIR, exist_ok=True)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(DB_DIR, 'db.sqlite')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Cria a pasta e o banco se não existirem
with app.app_context():
    db.create_all()

# Página inicial: busca de produtos
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Endpoint para realizar scraping e salvar no banco
@app.route('/buscar', methods=['POST'])
def buscar():
    termo = request.form.get('produto', '').strip()
    try:
        preco_min = float(request.form.get('preco_min', 0) or 0)

    except ValueError:
        preco_min = 0.0

    try:
        preco_max = float(request.form.get('preco_max', 1e9) or 1e9)
    except ValueError:
        preco_max = 1e9

    if not termo:
        return render_template('index.html', mensagem='Informe um produto para buscar.')

    produtos = scrape_mercado_livre(termo)
    produtos_filtrados = [p for p in produtos if preco_min <= (p.get('preco') or 0) <= preco_max]

    adicionados = 0
    for p in produtos_filtrados:
        exists = Produto.query.filter_by(nome=p['nome'], preco=p['preco']).first()
        if not exists:
            produto = Produto(
                nome=p['nome'],
                preco=p['preco'],
                avaliacao=p.get('avaliacao'),
                categoria=p.get('categoria', termo)
            )
            db.session.add(produto)
            adicionados += 1
    db.session.commit()

    return render_template('index.html', mensagem=f"{adicionados} produtos salvos com sucesso.")

# Dashboard com gráfico interativo
@app.route('/dashboard')
def dashboard():

    try:
        preco_min = float(request.args.get('min', 0) or 0)
    except ValueError:
        preco_min = 0.0

    try:
        preco_max = float(request.args.get('max', 1e9) or 1e9)
    except ValueError:
        preco_max = 1e9

    produtos = Produto.query.filter(Produto.preco >= preco_min, Produto.preco <= preco_max).all()
    dados = [
        {k: v for k, v in p.__dict__.items() if k != "_sa_instance_state"} for p in produtos]

    graph_json = None
    if dados:
        try:
            fig = px.scatter(
                dados, 
                x='preco',
                y='avaliacao',
                hover_data=['nome', 'categoria'],
                title='Preço vs Avaliação'
            )

            graph_json = json.dumps(fig, cls=ploty.utils.PlotlyJSONEncoder)
        except Exception as e:
            graph_json = None

    return render_template('dashboard.html', produtos=produtos, graphJSON=graphJSON, preco_min=preco_min, preco_max=preco_max )

# API JSON
@app.route('/api/produtos')
def api_produtos():
    produtos = Produto.query.all()
    return jsonify([{
        "id": p.id,
        "nome": p.nome,
        "preco": p.preco,
        "avaliacao": p.avaliacao,
        "categoria": p.categoria
    } for p in produtos])

# Roda o app
if __name__ == '__main__':
    app.run(debug=True)
