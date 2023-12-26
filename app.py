from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import csv

app = Flask(__name__)

# Função para ler o CSV e transformá-lo em uma lista de dicionários
def read_csv_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"O arquivo não foi encontrado: {filepath}")
    return pd.read_csv(filepath, sep=";").to_dict('records')

# Função para escrever dados de volta no arquivo CSV
def write_csv_file(filepath, data):
    pd.DataFrame(data).to_csv(filepath, sep=";", index=False)

# Caminho para o arquivo CSV
csv_file = os.path.join(os.getcwd(), 'instance', 'produtos.csv')


# Rota para exibir os dados
@app.route('/')
def index():
    try:
        data = read_csv_file(csv_file)
    except FileNotFoundError as e:
        return str(e), 500  # Retorna mensagem de erro com o código 500
    return render_template('index.html', data=data)

# Rota para editar um registro específico
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    data = read_csv_file(csv_file)
    product = next((item for item in data if str(item['id']) == id), None)
    if request.method == 'POST':
        # Atualiza o produto com os novos dados
        product['qtde_min'] = request.form['qtde_min']
        write_csv_file(csv_file, data)
        return redirect(url_for('index'))
    return render_template('edit.html', product=product)

# Rota para excluir um registro
@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    data = read_csv_file(csv_file)
    data = [item for item in data if str(item['id']) != id]
    write_csv_file(csv_file, data)
    return redirect(url_for('index'))

# Rota para adicionar um novo registro
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Recupera os dados do formulário
        new_id = request.form['id']
        new_qtde_min = request.form['qtde_min']
        
        # Lê os dados atuais e adiciona o novo registro
        data = read_csv_file(csv_file)
        data.append({'id': new_id, 'qtde_min': new_qtde_min})
        
        # Escreve os dados atualizados de volta no arquivo CSV
        write_csv_file(csv_file, data)
        return redirect(url_for('index'))
    return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)