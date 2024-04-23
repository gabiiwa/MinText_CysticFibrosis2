import csv
import logging
import math
from collections import defaultdict, Counter
from ast import literal_eval
from datetime import datetime


# Configuração do logging
logging.basicConfig(filename='indexador.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def preprocessar_termo(termo):
    """Transforma termos em letras maiúsculas ASCII, removendo não letras e termos curtos."""
    termo_ascii = ''.join(filter(str.isalpha, termo)).upper()
    return termo_ascii if len(termo_ascii) > 1 else None


def ler_configuracao(nome_arquivo):
    logging.info("Lendo arquivo de configuração: %s", nome_arquivo)
    config = {'LEIA': '', 'ESCREVA': ''}
    try:
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                chave, valor = linha.strip().split('=')
                config[chave] = valor
        logging.info("Configuração carregada com sucesso.")
    except Exception as e:
        logging.error("Falha ao ler arquivo de configuração: %s", str(e))
    return config

def calcular_tf_idf(lista_invertida, num_docs):
    tf_idf = defaultdict(dict)
    idf = {}
    for termo, docs in lista_invertida.items():
        # Pré-processamento do termo
        termo_processado = preprocessar_termo(termo)
        if not termo_processado:
            continue

        idf[termo_processado] = math.log(num_docs / len(docs))
        doc_counter = Counter(docs)
        for doc, freq in doc_counter.items():
            tf = freq / sum(doc_counter.values())
            tf_idf[termo_processado][doc] = tf * idf[termo_processado]
    return tf_idf

def salvar_modelo_vetorial(nome_arquivo, tf_idf):
    logging.info("Salvando modelo vetorial no arquivo: %s", nome_arquivo)
    try:
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            for termo, docs in tf_idf.items():
                for doc, peso in docs.items():
                    writer.writerow([termo, doc, peso])
        logging.info("Modelo vetorial salvo com sucesso.")
    except Exception as e:
        logging.error("Falha ao salvar modelo vetorial: %s", str(e))

if __name__ == '__main__':
    start_time = datetime.now()
    config = ler_configuracao('SRC/INDEX.CFG')
    if config['LEIA'] and config['ESCREVA']:
        # Leitura da lista invertida e o cálculo do TF-IDF
        with open(config['LEIA'], mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            lista_invertida = defaultdict(list)
            for rows in reader:
                termo, doc_ids = rows[0], literal_eval(rows[1].strip())
                # Aplicação do pré-processamento a cada termo já na leitura
                termo_processado = preprocessar_termo(termo)
                if termo_processado:
                    lista_invertida[termo_processado].extend(doc_ids)

        num_docs = len({doc_id for doc_ids in lista_invertida.values() for doc_id in doc_ids})

        tf_idf = calcular_tf_idf(lista_invertida, num_docs)
        salvar_modelo_vetorial(config['ESCREVA'], tf_idf)
        end_time = datetime.now()
        logging.info("Tempo total de indexador: %s", end_time - start_time)

    else:
        logging.error("Arquivo de configuração INDEX.CFG está incompleto ou ausente.")