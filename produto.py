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
    minimum_stock = db.Column(db.Integer, nullable=False) 

@app.route('/product_registration')
def product_registration():
    return render_template('product_registration.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    minimum_stock = request.form['minimum_stock']
    new_item = Item(name=name, quantity=0, minimum_stock=minimum_stock)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('product_registration'))
