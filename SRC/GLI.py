import xml.etree.ElementTree as ET
import csv
import logging
from collections import defaultdict
from datetime import datetime

# Configuração do Logging
logging.basicConfig(filename='gerador_lista_invertida.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def ler_configuracao(nome_arquivo):
    logging.info("Lendo arquivo de configuração: %s", nome_arquivo)
    config = {'LEIA': [], 'ESCREVA': None}
    try:
        with open(nome_arquivo, 'r') as f:
            for linha in f:
                if linha.startswith('LEIA'):
                    _, path = linha.strip().split('=')
                    config['LEIA'].append(path)
                elif linha.startswith('ESCREVA'):
                    _, path = linha.strip().split('=')
                    config['ESCREVA'] = path
        logging.info("Configuração carregada com sucesso.")
    except Exception as e:
        logging.error("Falha ao ler arquivo de configuração: %s", str(e))
    return config

def processar_arquivos_xml(arquivos):
    lista_invertida = defaultdict(list)
    total_docs = 0
    for arquivo in arquivos:
        logging.info("Processando arquivo XML: %s", arquivo)
        try:
            tree = ET.parse(arquivo)
            root = tree.getroot()
            for record in root.findall('.//RECORD'):
                record_num = record.find('RECORDNUM').text
                abstract = record.find('ABSTRACT') or record.find('EXTRACT')
                if abstract is not None:
                    total_docs += 1
                    palavras = abstract.text.upper().split()
                    for palavra in set(palavras):  # Remove duplicatas para contar apenas uma vez por documento
                        lista_invertida[palavra].append(record_num)
            logging.info("Arquivo %s processado com sucesso.", arquivo)
        except Exception as e:
            logging.error("Erro ao processar o arquivo %s: %s", arquivo, str(e))
    logging.info("Total de documentos processados: %d", total_docs)
    return lista_invertida

def salvar_lista_invertida(arquivo_saida, lista_invertida):
    logging.info("Salvando lista invertida no arquivo: %s", arquivo_saida)
    try:
        with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            for palavra, registros in lista_invertida.items():
                writer.writerow([palavra, registros])
        logging.info("Lista invertida salva com sucesso.")
    except Exception as e:
        logging.error("Falha ao salvar a lista invertida: %s", str(e))

if __name__ == '__main__':
    start_time = datetime.now()
    config = ler_configuracao('SRC/GLI.CFG')
    if config['LEIA'] and config['ESCREVA']:
        lista_invertida = processar_arquivos_xml(config['LEIA'])
        salvar_lista_invertida(config['ESCREVA'], lista_invertida)
        end_time = datetime.now()
        logging.info("Tempo total de processamento: %s", end_time - start_time)
    else:
        logging.error
