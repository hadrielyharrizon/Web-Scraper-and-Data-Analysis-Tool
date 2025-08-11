from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(300), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    avaliacao = db.Column(db.Float, nullable=True)
    categoria = db.Column(db.String(100), nullable=False)
