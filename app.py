from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///produtos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    qtd_minima = db.Column(db.Integer, nullable=False)
    qtd_disponivel = db.Column(db.Integer, default=0)  


with app.app_context():
    db.create_all()

@app.route('/produtos')
def index():
    produtos = Produto.query.all()
    return render_template('index.html', produtos=produtos)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome_produto = request.form['nome']
        qtd_minima_produto = int(request.form['qtd_minima'])  
        produto = Produto(nome=nome_produto, qtd_minima=qtd_minima_produto)
        db.session.add(produto)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('cadastrar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    produto = Produto.query.get_or_404(id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.qtd_minima = int(request.form['qtd_minima'])
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('editar.html', produto=produto)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/entrada/<int:id>', methods=['POST'])
def entrada_produto(id):
    produto = Produto.query.get_or_404(id)
    quantidade_entrada = int(request.form['quantidade_entrada'])
    produto.qtd_disponivel += quantidade_entrada
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/saida/<int:id>', methods=['POST'])
def saida_produto(id):
    produto = Produto.query.get_or_404(id)
    quantidade_saida = int(request.form['quantidade_saida'])
    if quantidade_saida <= produto.qtd_disponivel:
        produto.qtd_disponivel -= quantidade_saida
        db.session.commit()
    else:
        # Tratar erro, não há quantidade suficiente
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
