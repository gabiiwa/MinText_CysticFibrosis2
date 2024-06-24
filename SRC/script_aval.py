import pandas as pd
import numpy as np
import math
import logging
from collections import defaultdict
import ast
from nltk.stem.porter import PorterStemmer
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, average_precision_score

def processar_resultados(path):
    df = pd.read_csv(path, delimiter=';')
    df['lista'] = df['lista'].apply(ast.literal_eval)
    return df

def processar_esperados(path):
    df = pd.read_csv(path, delimiter=';')
    df['DocVotes'] = df['DocVotes'].astype(int)
    return df


# Converter lista de resultados para DataFrame
def expandir_resultados(df):
    rows = []
    for _, row in df.iterrows():
        for doc in row['lista']:
            rows.append({'QueryNumber': row['id_consulta'], 'DocNumber': int(doc[1].strip()), 'Score': doc[2]})
    return pd.DataFrame(rows)

# Ajustar os esperados para incluir os scores
def preparar_esperados(df, resultados):
    df = df.merge(resultados[['QueryNumber', 'DocNumber', 'Score']], on=['QueryNumber', 'DocNumber'], how='left')
    df['Score'] = df['Score'].fillna(0)
    df['Relevance'] = np.where(df['DocVotes'] > 0, 1, 0)  # Assumindo relevância como binária baseada em DocVotes > 0
    return df

# Função para calcular Precision@K
def precision_at_k(resultados, k):
    relevantes = resultados.head(k)['Relevance'].sum()
    return relevantes / k

# Função para calcular Mean Average Precision (MAP)
def mean_average_precision(resultados):
    aps = []
    for query in resultados['QueryNumber'].unique():
        temp = resultados[resultados['QueryNumber'] == query]
        aps.append(average_precision_score(temp['Relevance'], temp['Score']))
    return np.mean(aps)

# Função para calcular Mean Reciprocal Rank (MRR)
def mean_reciprocal_rank(resultados):
    mrr = 0
    for query in resultados['QueryNumber'].unique():
        temp = resultados[resultados['QueryNumber'] == query]
        temp = temp[temp['Relevance'] == 1]
        if not temp.empty:
            mrr += 1 / (temp.index[0] + 1)
    return mrr / len(resultados['QueryNumber'].unique())

# Função para plotar o gráfico de 11 pontos de precisão e recall
def plot_precisao_recall_11pontos(resultados):
    precision, recall, _ = precision_recall_curve(resultados['Relevance'], resultados['Score'])
    plt.figure(figsize=(8, 5))
    plt.plot(recall, precision, marker='o', linestyle='-', color='b')
    plt.title('Gráfico de 11 pontos de precisão e recall')
    plt.xlabel('Recall')
    plt.ylabel('Precisão')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    resultados_df = processar_resultados("../RESULTS/RESULTADOS.csv")
    esperados_df = processar_esperados("../RESULTS/resultados_esperados.csv")
    resultados_expandidos = expandir_resultados(resultados_df)
    print("resultados expandidos: \n", resultados_expandidos)
    resultados_completos = preparar_esperados(esperados_df, resultados_expandidos)
    
    # Calcular e imprimir Precision@5 e Precision@10 para uma consulta exemplo (00001)
    print(f"Precision@5: {precision_at_k(resultados_completos[resultados_completos['QueryNumber'] == '00001'], 5)}")
    print(f"Precision@10: {precision_at_k(resultados_completos[resultados_completos['QueryNumber'] == '00001'], 10)}")
    
    # Calcular e imprimir MAP e MRR para todo o dataset
    print(f"MAP: {mean_average_precision(resultados_completos)}")
    print(f"MRR: {mean_reciprocal_rank(resultados_completos)}")
    
    # # Plotar o gráfico de 11 pontos de precisão e recall para uma consulta exemplo (00001)
    # plot_precisao_recall_11pontos(resultados_completos[resultados_completos['QueryNumber'] == '00001'])
