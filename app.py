from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf.csrf import CSRFProtect
import pandas as pd
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ewwegrgr2545'
csrf = CSRFProtect(app)


def read_csv_file(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"O arquivo não foi encontrado: {filepath}")
    return pd.read_csv(filepath, sep=";").to_dict('records')

def read_csv(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"O arquivo não foi encontrado: {filepath}")
    return pd.read_csv(filepath, sep=";")

def write_csv_file(filepath, data):
    pd.DataFrame(data).to_csv(filepath, sep=";", index=False)

@app.route('/prod')
def index():
    try:
        csv_file = os.path.join(os.getcwd(), 'instance', 'produtos.csv')
        data = read_csv_file(csv_file)
    except FileNotFoundError as e:
        return str(e), 500  
    return render_template('index.html', data=data)

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    csv_file = os.path.join(os.getcwd(), 'instance', 'produtos.csv')
    data = read_csv_file(csv_file)
    product = next((item for item in data if str(item['id']) == id), None)
    if request.method == 'POST':
        # Atualiza o produto com os novos dados
        product['qtde_min'] = request.form['qtde_min']
        write_csv_file(csv_file, data)
        return redirect(url_for('index'))
    return render_template('edit.html', product=product)

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    csv_file = os.path.join(os.getcwd(), 'instance', 'produtos.csv')
    data = read_csv_file(csv_file)
    data = [item for item in data if str(item['id']) != id]
    write_csv_file(csv_file, data)
    return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Recupera os dados do formulário
        new_id = request.form['id']
        new_qtde_min = request.form['qtde_min']
        
        # Lê os dados atuais e adiciona o novo registro
        csv_file = os.path.join(os.getcwd(), 'instance', 'produtos.csv')
        data = read_csv_file(csv_file)
        data.append({'id': new_id, 'qtde_min': new_qtde_min})
        
        # Escreve os dados atualizados de volta no arquivo CSV
        write_csv_file(csv_file, data)

        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/estoque')
def estoque():
    # Ler os dados dos arquivos CSV
    produtos_df = read_csv(os.path.join(os.getcwd(), 'instance', 'produtos.csv'))
    entradas_df = read_csv(os.path.join(os.getcwd(), 'instance', 'entradas.csv'))
    saidas_df = read_csv(os.path.join(os.getcwd(), 'instance', 'saida.csv'))

    # Agrupar e somar as quantidades por ID
    total_entradas = entradas_df.groupby('id')['Qtd'].sum()
    total_saidas = saidas_df.groupby('id')['Qtd'].sum()

    # Fazer um DataFrame a partir do estoque de produtos e adicionar as colunas de entrada e saída
    estoque_df = produtos_df.set_index('id')
    estoque_df['total_entradas'] = total_entradas
    estoque_df['total_saidas'] = total_saidas
    estoque_df['total_entradas'] = estoque_df['total_entradas'].fillna(0)  # Preencher NaN com 0
    estoque_df['total_saidas'] = estoque_df['total_saidas'].fillna(0)  # Preencher NaN com 0

    # Calcular o resultado (qtd_min - (entrada - saída))
    estoque_df['resultado'] = (estoque_df['total_entradas'] - estoque_df['total_saidas'])

    # Resetar o índice para enviar ao template
    estoque_df = estoque_df.reset_index()

    # Converter o DataFrame para dicionário para renderização no template
    estoque_data = estoque_df.to_dict('records')

    return render_template('estoque.html', data=estoque_data)

@app.route('/entradas')
def entradas():
    entrada_file = os.path.join(os.getcwd(), 'instance', 'entradas.csv')
    data_entradas = read_csv_file(entrada_file)
    return render_template('entradas.html', data=data_entradas)

@app.route('/saidas')
def saidas():
    saida_file = os.path.join(os.getcwd(), 'instance', 'saida.csv')
    data_saidas = read_csv_file(saida_file)
    return render_template('saidas.html', data=data_saidas)


@app.route('/repor_estoque/<id>', methods=['POST'])
def repor_estoque(id):
    try:
        # Ler os dados dos arquivos CSV
        entradas_csv = os.path.join(os.getcwd(), 'instance', 'entradas.csv')
        produtos_df = read_csv(os.path.join(os.getcwd(), 'instance', 'produtos.csv'))
        entradas_df = read_csv(entradas_csv)

        # Encontrar o produto correspondente pelo ID e obter a qtd_min
        produto = produtos_df.loc[produtos_df['id'] == id]
        if produto.empty:
            flash('Produto não encontrado.', 'danger')
            return redirect(url_for('estoque'))
        
        qtd_min = produto.iloc[0]['qtde_min']  

        # Criar o novo registro para adicionar ao DataFrame de entradas
        nova_entrada = {'id': id, 'Qtd': qtd_min, 'Data': datetime.now().strftime('%d/%m/%Y')}
        entradas_df = entradas_df.append(nova_entrada, ignore_index=True)
        
        # Escrever o DataFrame atualizado de volta para o CSV
        write_csv_file(entradas_csv, entradas_df)
        
        flash('Reposição automática realizada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao repor estoque: {e}', 'danger')

    return redirect(url_for('estoque'))

if __name__ == '__main__':
    app.run(debug=True)