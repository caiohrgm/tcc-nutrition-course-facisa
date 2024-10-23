import os, sys
import openpyxl
import numpy as np
import pandas as pd
import tkinter as tk
import seaborn as sns
from datetime import datetime
from tkinter import filedialog
import matplotlib.pyplot as plt

from utils import clean_height, clean_weight, check_compulsion, check_ortorexia, check_nutrition_status


# Ensure the necessary directories exist
os.makedirs('./data', exist_ok=True)
os.makedirs('../reports/boxplots', exist_ok=True)
os.makedirs('../reports/correlations', exist_ok=True)


def main(input_file):
    # Use the provided input file
    df = pd.read_excel(input_file, engine='openpyxl')

    """ PREPARAÇÃO DOS DADOS """
    print("Iniciando preparação dos dados...")
    # Filtra se o consentimento foi dado e remvoe a coluna de consentimento (só por garantia)
    consentiment_column = df.columns[1]
    filtered_df = df[df[consentiment_column] == 'Li e concordo em participar da pesquisa.'].drop(['Carimbo de data/hora', 'Cidade e Estado:', consentiment_column], axis =1)

    # Renomeando algumas colunas:
    filtered_df.columns.values[0] = 'idade'
    filtered_df.columns.values[1] = 'peso'
    filtered_df.columns.values[2] = 'altura'
    filtered_df.columns.values[3] = 'sexo'
    filtered_df.columns.values[4] = 'gênero'
    filtered_df.columns.values[5] = 'etnia'
    q = 1
    for i in range(len(filtered_df.columns)):
        if i >= 26:

            filtered_df.columns.values[i] = str(q)
            q += 1

    # Tratando coluna da idade:    
    filtered_df['idade'] = filtered_df['idade'].apply(lambda x: ''.join(filter(str.isdigit, str(x))) if pd.notna(x) else x)
    filtered_df['idade'] = pd.to_numeric(filtered_df['idade'], errors='coerce').astype('Int64')

    # Tratando coluna peso:
    # Aplicar a função de limpeza
    filtered_df['peso'] = filtered_df['peso'].apply(clean_weight)

    # Tratando coluna altura:
    filtered_df['altura'] = filtered_df['altura'].apply(clean_height)

    filtered_df.to_csv("../data/filtered_data.csv", index=False)

    # Iterando o df linha alinha (usuario a usuario)
    df = filtered_df.copy(deep=True)
    size = df.shape[0]

    print("Dados preparados e filtrados. Iniciando criação das colunas do estudo...")
    new_df = pd.DataFrame()
    for i in range(size):
        row =  filtered_df.iloc[i].to_frame().transpose()

        # Dados socio-econômicos
        row_social = row.iloc[:, 0:10]       # 0:11 includes columns from position 0 to 10
        
        idade = row_social['idade'].values[0]
        peso = row_social['peso'].values[0]
        altura = row_social['altura'].values[0]
        
        # Dados de Compulsão alimentar
        row_compulsion = row.iloc[:, 10:26]   # 10:26 includes columns from position 10 to 25
        row_compulsion = row_compulsion.apply(lambda col: col.str.replace(r'[^1234]', '', regex=True))
        total_compulsion, _ = check_compulsion(row_compulsion)
        row['indice_compulsao'] = [total_compulsion]
        
        # Dados Ortorexia
        row_ortorexia = row.iloc[:, 26:41]   # 26:41 includes columns from position 26 to 40
        row_ortorexia.columns = row_ortorexia.columns.str.extract(r'(\d+)')[0]
        total_ortorexia = check_ortorexia(row_ortorexia)
        row['indice_ortorexia'] = [total_ortorexia]

        # Dados estado nutricional:
        nutrition_status, nutrition_status_ref  = check_nutrition_status(peso, altura)
        row['estado_nutricional'] = [nutrition_status]
        row['estado_nutricional_ref'] = [nutrition_status_ref]
        new_df = pd.concat([new_df, row])

    current_date = current_date = datetime.now().strftime("%d_%m_%y")
    try:
        new_df.to_excel(f'../data/final_data_output_{current_date}.xlsx', index=False, engine='openpyxl')
        print("Dados totalmente preparados e salvos.")
    except:
        print("Erro ao salvar os dados.")

    """ INFORMAÇÕES DA AMOSTRA"""
    print("Iniciando estudo dos dados da amostra...")
    sample_data_df = new_df.copy(deep=True)

    # Convert columns to numeric
    sample_data_df['idade'] = pd.to_numeric(sample_data_df['idade'].astype(str).str.strip(), errors='coerce')
    sample_data_df['peso'] = pd.to_numeric(sample_data_df['peso'].astype(str).str.strip(), errors='coerce')

    # Replace commas with dots in the altura column and convert to numeric
    sample_data_df['altura'] = pd.to_numeric(sample_data_df['altura'].astype(str).str.replace(',', '.', regex=False).str.strip(), errors='coerce')

    filter_df = sample_data_df[['idade', 'peso', 'altura']]

    filter_df['idade'].plot(kind='box', figsize=(8, 6))
    plt.title('Distribuição da Idade dos entrevistados')
    plt.savefig('../reports/boxplots/idade.png')

    filter_df['peso'].plot(kind='box', figsize=(8, 6))
    plt.title('Distribuição da Peso dos entrevistados')
    plt.savefig('../reports/boxplots/peso.png')

    filter_df['altura'].plot(kind='box', figsize=(8, 6))
    plt.title('Distribuição da Altura dos entrevistados')
    plt.savefig('../reports/boxplots/altura.png')

    """ ANÁLISE ESTATÍSTICA """
    correlation_compulsao = np.round(new_df['estado_nutricional_ref'].corr(new_df['indice_compulsao']),4)
    corr = 0
    if correlation_compulsao > 0.5:
        corr = 'positiva forte'
    elif correlation_compulsao > 0 and correlation_compulsao <= 0.5:
        corr  =  'positiva fraca'
    elif correlation_compulsao == 0:
        corr = 'não existe'
    elif correlation_compulsao < 0 and correlation_compulsao >= -0.5:
        corr = 'negativa fraca'
    else:
        corr = 'negativa fraca' 
    print(f"Correlação entre estado nutricional e compulsão: {corr} ({correlation_compulsao}).")

    # Create a scatter plot with a regression line
    plt.figure(figsize=(8, 6))
    sns.regplot(x='estado_nutricional_ref', y='indice_compulsao', data=new_df)

    # Show the plot
    plt.title('Correlação Estado Nutricional X Índice de Compulsão Alimentar')
    plt.xlabel('estado nutricional')
    plt.ylabel('índice de compulsão')
    plt.savefig('../reports/correlations/estado_nutricional_com_compulsao.png')

    correlation_ortorexia = np.round(new_df['estado_nutricional_ref'].corr(new_df['indice_ortorexia']),4)

    corr = 0
    if correlation_ortorexia > 0.5:
        corr = 'positiva forte'
    elif correlation_ortorexia > 0 and correlation_ortorexia <= 0.5:
        corr  =  'positiva fraca'
    elif correlation_ortorexia == 0:
        corr = 'não existe'
    elif correlation_ortorexia < 0 and correlation_ortorexia >= -0.5:
        corr = 'negativa fraca'
    else:
        corr = 'negativa fraca' 
    print(f"Correlação entre estado nutricional e ortorexia: {corr} ({correlation_ortorexia}).")

    # Create a scatter plot with a regression line
    plt.figure(figsize=(8, 6))
    sns.regplot(x='estado_nutricional_ref', y='indice_ortorexia', data=new_df)

    # Show the plot
    plt.title('Correlação Estado Nutricional X Índice de Ortorexia')
    plt.xlabel('estado nutricional')
    plt.ylabel('índice de ortorexia')
    plt.savefig('../reports/correlations/estado_nutricional_com_ortorexia.png')
    print("Estudo concluído.")

def select_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(title='Selecione Seu arquivo', filetypes=[('Excel Files', '*.xlsx;*.xls')])
    return file_path


if __name__ == "__main__":
    input_file = select_file()

    if not input_file:
        print("Nenhum arquivo encontrado/selecionado.")
        sys.exit()

    main(input_file)