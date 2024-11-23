import ollama
import pandas as pd
import re
import json
import os

# Configuração do modelo e leitura do prompt
llm_model = 'llama3.2:latest'
prompt = open('promptFullChat.txt', 'r', encoding="utf8").read()

# Criar pasta de log, se não existir
os.makedirs("log", exist_ok=True)
log_file_path = "log/errors.json"

# Leitura dos dados
data = pd.read_json('../data/filtered_data.json')

# Remover a coluna 'TARGET' se já existir
if 'TARGET' in data.columns:
    data.drop('TARGET', axis=1, inplace=True)

# Lista de respostas válidas
valid_responses = ['SRI', 'SSA', 'SUPORTE NIVEL 1', 'SUPORTE NIVEL 2', 'ICC', 'CIDC', 'SSI']

# Criar uma nova coluna 'TARGET' no DataFrame
data['TARGET'] = None

# Lista para armazenar erros
error_log = []

unique_ids = data['HD_TICKET_ID'].unique()

for key in unique_ids:
    chat = ''
    filtered_data = data[data['HD_TICKET_ID'] == key]

    for index, row in filtered_data.iterrows():
        chat += f"{index+1} message: {row['COMMENT']}\n"

    prompt = prompt.replace('message', chat)
    response = ollama.chat(model=llm_model, messages=[
        {
            'role': 'user',
            'content': chat,
        }
    ])
