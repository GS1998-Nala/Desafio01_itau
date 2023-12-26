from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'senha11314314'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    minimum_stock = db.Column(db.Integer, nullable=False)  # New field

@app.route('/')
def index():
    items = Item.query.all()
    # Adiciona o ícone de status para cada item.
    for item in items:
        item.status_icon = '<i class="fas fa-circle" style="color: green;"></i>' if item.quantity > item.minimum_stock else '<i class="fas fa-circle" style="color: red;"></i>'
    return render_template('index.html', items=items)



@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    quantity = request.form.get('quantity')
    minimum_stock = request.form.get('minimum_stock')  # Get minimum_stock from form

    new_item = Item(name=name, quantity=quantity, minimum_stock=minimum_stock)
    db.session.add(new_item)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    # Pega a quantidade e a quantidade mínima do formulário.
    quantity = request.form.get('quantity', type=int)
    minimum_stock = request.form.get('minimum_stock', type=int)
    
    item = Item.query.get(id)
    if item:
        item.quantity = quantity
        item.minimum_stock = minimum_stock  # Atualiza a quantidade mínima também.
        db.session.commit()
        
        # Retorna um ícone dependendo da comparação entre quantidade e quantidade mínima.
        status_icon = '<i class="fas fa-circle" style="color: green;"></i>' if quantity > minimum_stock else '<i class="fas fa-circle" style="color: red;"></i>'
        return redirect(url_for('index', status_icon=status_icon))
    else:
        return "Error: No such item found.", 404


@app.route('/delete/<int:id>')
def delete(id):
    item = Item.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return "Error: No such item found.", 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)