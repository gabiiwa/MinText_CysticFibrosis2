"""
# Regras Logging:
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

# Configuração do logging
logging.basicConfig(filename='src/processador_de_consultas.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
#%%
def ler_configuracao(nome_arquivo):
    logging.info("Lendo arquivo de configuracao: %s", nome_arquivo)
    # print("Lendo arquivo de configuracao "+ nome_arquivo)
    config = {}
    try:
        with open(nome_arquivo, "r") as cfg_file:
            for line in cfg_file:
                print(f"line:{line}")
                key, value = line.strip().split('=')
                config[key] = value
        print(f"config:{config}")
        logging.info("Arquivo de configuração lido com sucesso.")
    except Exception as e:
        logging.error("Erro ao ler arquivo de configuração: %s", str(e))
    return config
#%%
def processar_consultas(entrada_xml, saida_consultas, saida_esperados):
    logging.info("Processando consultas a partir do arquivo: %s", entrada_xml)
    inicio = datetime.now()
    try:
        tree = ET.parse(entrada_xml)
        print(f"\n tree:{tree} \n")
        root = tree.getroot()
        queries, expected = [], []

        # print(f"Query:{root.findall('QUERY')}")
        for query in root.findall('QUERY'):
            # print(f"query:{query}")
            query_number = query.find('QueryNumber').text
            query_text = query.find('QueryText').text.upper().replace(";", "")
            queries.append([query_number, query_text])
            # print(f"\n Queries:{queries}\n")
            # print(f"results:{query.find('Results').text}")

            # print(f"records and items:{query.findall('Records/Item')}")
            for item in query.findall('Records/Item'):
                if item.attrib['score'] != '0':
                    # print(f"item documento:{item.text}")
                    expected.append([query_number, item.text, item.attrib['score']])#'QueryNumber','DocNumber','DocVotes'
        
        # print(f"Queries:{queries}")
        salvar_csv(saida_consultas, queries, ['QueryNumber', 'QueryText'])
        salvar_csv(saida_esperados, expected, ['QueryNumber', 'DocNumber', 'DocVotes'])
        fim = datetime.now()
        logging.info("Consultas processadas e salvas com sucesso. Tempo de processamento: %s", fim - inicio)
    except Exception as e:
        logging.error("Erro ao processar consultas: %s", str(e))
#%%
def salvar_csv(nome_arquivo, dados, cabecalho):
    logging.info("Salvando dados no arquivo CSV: %s", nome_arquivo)
    try:
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as f:
            print(f"nome arquivo:{nome_arquivo}")
            writer = csv.writer(f, delimiter=';')
            writer.writerow(cabecalho)
            writer.writerows(dados)
        logging.info("Dados salvos com sucesso no arquivo: %s", nome_arquivo)
    except Exception as e:
        logging.error("Erro ao salvar dados no arquivo CSV: %s", str(e))
#%%
if __name__ == "__main__":
    logging.info("Início do Processador de Consultas")
    # with open("PC.CFG", "r") as cfg_file:
    #     for line in cfg_file:
    #         print(f"line:{line}")
    config = ler_configuracao("PC.CFG")
    if config:
        processar_consultas(config['LEIA'], config['CONSULTAS'], config['ESPERADOS'])
    logging.info("Processador de Consultas finalizado")


# %%
