import ollama
import pandas as pd
import re
import json
import os

# Configuração do modelo e leitura do prompt
llm_model = 'llama3.2:latest'
prompt = open('prompt.txt', 'r', encoding="utf8").read()

# Criar pasta de log, se não existir
os.makedirs("log", exist_ok=True)
log_file_path = "log/errors.json"

# Leitura dos dados
data = pd.read_json('../data/filtered_data.json')

# Remover a coluna 'TARGET' se já existir
if 'TARGET' in data.columns:
    data.drop('TARGET', axis=1, inplace=True)

# Lista de respostas válidas
valid_responses = ['SRI', 'SSA', 'SUPORTE NIVEL 1', 'SUPORTE NIVEL 2', 'ICC', 'CIDC', 'SSI', 'INVALIDA']

# Criar uma nova coluna 'TARGET' no DataFrame
data['TARGET'] = None

# Lista para armazenar erros
error_log = []

# Iterar sobre as mensagens e analisar
for index, row in data.iterrows():
    question = row['COMMENT']  # Pega o texto da mensagem
    full_prompt = prompt.replace('message', question)

    # Envia o prompt para o modelo
    response = ollama.chat(model=llm_model, messages=[
        {
            'role': 'user',
            'content': full_prompt,
        }
    ])

    # Normaliza e remove pontuações da resposta
    OllamaResponse = response['message']['content'].strip().upper()
    OllamaResponse = re.sub(r'[^\w\s]', '', OllamaResponse)

    # Valida e armazena a resposta no DataFrame
    if OllamaResponse in valid_responses:
        data.at[index, 'TARGET'] = OllamaResponse  # Resposta válida
    else:
        print(f"Resposta inválida: {OllamaResponse}")
        error_log.append({
            "ID": row.get('ID', index),
            "QUESTION": question,
            "RESPONSE": OllamaResponse,
        })
        data.at[index, 'TARGET'] = "erro"  # Marcar como inválida

if error_log:
    with open(log_file_path, 'w', encoding='utf-8') as log_file:
        json.dump(error_log, log_file, ensure_ascii=False, indent=4)

# Converter Timestamps para strings antes de salvar
def convert_timestamps(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj

# Salvar o DataFrame atualizado
data_list = data.to_dict(orient='records')
with open('../data/analyzed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=4, default=convert_timestamps)

print('Processamento concluído.')
