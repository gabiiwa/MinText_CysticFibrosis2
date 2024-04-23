"""
# Regras logger:
#     1. Identificar quando iniciaram suas operações
#     2. Identificar quando iniciam cada parte de seu processamento
#         a. Ler arquivo de configuração
#         b. Ler arquivo de dados
#     3. Identificar quantos dados foram lidos
#     4. Identificar quando terminaram os processamentos
#     5. Calcular os tempos médios de processamento de consultas, documento e palavras, de acordo
#     com o programa sendo usado
#     6. Identificar erros no processamento, caso aconteçam
"""
#%%
import csv
import xml.etree.ElementTree as ET
import logging
from datetime import datetime

# Configuração do logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='processador_de_consultas.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
#%%
def ler_configuracao(nome_arquivo):
    logging.info("Lendo arquivo de configuracao: %s", nome_arquivo)

    config = {}
    try:
        with open(nome_arquivo, "r") as cfg_file:
            for line in cfg_file:
                key, value = line.strip().split('=')
                config[key] = value

        logging.info("Arquivo de configuração lido com sucesso.")
    except Exception as e:
        logging.error("Erro ao ler arquivo de configuração: %s", str(e))
    return config
#%%
def processar_consultas(entrada_xml, saida_consultas, saida_esperados):
    logger.info("Processando consultas a partir do arquivo: %s", entrada_xml)
    inicio = datetime.now()
    try:
        tree = ET.parse(entrada_xml)
        root = tree.getroot()
        queries, expected = [], []

        for query in root.findall('QUERY'):
            query_number = query.find('QueryNumber').text
            query_text = query.find('QueryText').text.upper().replace(";", "")
            queries.append([query_number, query_text])
            for item in query.findall('Records/Item'):
                if item.attrib['score'] != '0':
                    expected.append([query_number, item.text, item.attrib['score']])#'QueryNumber','DocNumber','DocVotes'

        salvar_csv(saida_consultas, queries, ['QueryNumber', 'QueryText'])
        salvar_csv(saida_esperados, expected, ['QueryNumber', 'DocNumber', 'DocVotes'])
        fim = datetime.now()
        logger.info("Consultas processadas e salvas com sucesso. Tempo de processamento: %s", fim - inicio)
    except Exception as e:
        logger.error("Erro ao processar consultas: %s", str(e))
#%%
def salvar_csv(nome_arquivo, dados, cabecalho):
    logger.info("Salvando dados no arquivo CSV: %s", nome_arquivo)
    try:
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(cabecalho)
            writer.writerows(dados)
        logger.info("Dados salvos com sucesso no arquivo: %s", nome_arquivo)
    except Exception as e:
        logger.error("Erro ao salvar dados no arquivo CSV: %s", str(e))
#%%
if __name__ == "__main__":
    logger.info("Início do Processador de Consultas")
    config = ler_configuracao("SRC/PC.CFG")
    if config:
        start_time = datetime.now()
        processar_consultas(config['LEIA'], config['CONSULTAS'], config['ESPERADOS'])
        end_time = datetime.now()

    logger.info("Processador de Consultas finalizado")
    logging.info("Tempo total do processador de consulta: %s", end_time - start_time)



# %%
