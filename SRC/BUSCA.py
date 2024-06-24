import csv
import logging
from collections import defaultdict
import re
from datetime import datetime


# Configuração do logging
logging.basicConfig(filename='buscador.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def ler_configuracao(nome_arquivo):
    logging.info("Lendo arquivo de configuração: %s", nome_arquivo)
    config = {}
    try:
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                chave, valor = linha.strip().split('=')
                config[chave] = valor
        logging.info("Configuração carregada com sucesso.")
    except Exception as e:
        logging.error("Falha ao ler arquivo de configuração: %s", str(e))
    return config

def ler_modelo_vetorial(nome_arquivo):
    modelo = defaultdict(dict)
    try:
        with open(nome_arquivo, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                termo, doc_id, peso = row
                modelo[termo][doc_id] = float(peso)
        logging.info("Modelo vetorial carregado com sucesso.")
    except Exception as e:
        logging.error("Falha ao carregar modelo vetorial: %s", str(e))
    return modelo

def ler_consultas(nome_arquivo):
    consultas = {}
    with open(nome_arquivo, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for linha in reader:
            consulta_id = linha['QueryNumber']
            # Remover caracteres especiais, números e transformar em maiúsculas
            texto_consulta = re.sub(r'[^A-Za-z\s]', '', linha['QueryText'].upper())
            # Dividir o texto em palavras e filtrar palavras com menos de 2 letras
            palavras = [palavra for palavra in texto_consulta.split() if len(palavra) > 1]
            consultas[consulta_id] = palavras
    return consultas

def buscar(modelo, consultas):
    resultados = {}
    for consulta_id, termos in consultas.items():
        ranking = defaultdict(float)
        for termo in termos:
            if termo in modelo:
                for doc_id, peso in modelo[termo].items():
                    ranking[doc_id] += peso
        resultados[consulta_id] = sorted(ranking.items(), key=lambda item: item[1], reverse=True)
    return resultados

def escrever_resultados(nome_arquivo, resultados,cabecalho):
    try:
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(cabecalho)
            for consulta_id, docs in resultados.items():
                linha = [consulta_id, [(i+1, doc[0], doc[1]) for i, doc in enumerate(docs)]]
                writer.writerow(linha)
        logging.info("Resultados da busca salvos com sucesso.")
    except Exception as e:
        logging.error("Falha ao salvar resultados da busca: %s", str(e))

if __name__ == '__main__':
    config = ler_configuracao('SRC/BUSCA.CFG')

    start_time = datetime.now()
    modelo_vetorial = ler_modelo_vetorial(config['MODELO'])
    consultas = ler_consultas(config['CONSULTAS'])  
    resultados = buscar(modelo_vetorial, consultas)
    escrever_resultados(config['RESULTADOS'], resultados,['id_consulta','lista'])
    end_time = datetime.now()

    logging.info("Tempo total do buscador: %s", end_time - start_time)
