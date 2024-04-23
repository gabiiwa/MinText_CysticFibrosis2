#!/bin/bash

# Instala as dependências do Python
pip3 install -r requirements.txt

# Inicia a contagem do tempo
start_time=$(date +%s%N)

# Executa os scripts 
python SRC/PC.py
python SRC/GLI.py
python SRC/INDEX.py
python SRC/BUSCA.py

# Finaliza a contagem do tempo
end_time=$(date +%s%N)

# Calcula a duração total e exibe
duration=$(echo "scale=4; ($end_time - $start_time) / 1000000000" | bc)
echo "Tempo total de execução: $duration segundos"