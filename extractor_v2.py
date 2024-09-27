import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time
import re
import json

class Extractor_v2:

    def __init__(self, path):
        self.data = self.load_data(path)

    def load_data(self, path):
        return pd.read_json(path)

    def save_data(self, path):
        self.data = self.data.fillna('')

        # Converter objetos Timestamp para strings
        self.data = self.data.applymap(lambda x: x.isoformat() if isinstance(x, pd.Timestamp) else x)

        data_list = self.data.to_dict(orient='records')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)

    def order_by_HD_TICKET(self):
        self.data = self.data.sort_values(by=["HD_TICKET_ID", "TIMESTAMP"])

    def drop_columns(self):
        self.data = self.data.drop(
            columns=['COMMENT_LOC', 'LOCALIZED_DESCRIPTION',
                     'LOCALIZED_OWNERS_ONLY_DESCRIPTION', 'MAILED', 'MAILED_TIMESTAMP', 'MAILER_SESSION',
                     'NOTIFY_USERS', 'VIA_EMAIL', 'OWNERS_ONLY', 'RESOLUTION_CHANGED', 'SYSTEM_COMMENT',
                     'TICKET_DATA_CHANGE', 'VIA_SCHEDULED_PROCESS', 'VIA_IMPORT', 'VIA_BULK_UPDATE'])

    def fill_na(self):
        self.data = self.data.fillna(np.nan)

    @staticmethod
    def extract_comment_text(comment_html):
        if comment_html is None:
            return ''
        if isinstance(comment_html, str) and (comment_html.strip().startswith('<') or comment_html.strip().startswith('&lt;')):
            # Verifica se parece ser HTML
            try:
                soup = BeautifulSoup(comment_html, 'html.parser')
                return soup.get_text()
            except Exception as e:
                return f"Erro ao extrair texto de COMMENT: {e}"
        else:
            # Caso contrário, retorna o texto bruto
            return comment_html

    def show_data(self):
        print(self.data)

    def apply_comment_extraction(self):
        self.data['COMMENT'] = self.data['COMMENT'].apply(self.extract_comment_text)

    def drop_empty_comments(self):
        self.data = self.data[self.data['COMMENT'] != ''].dropna()

    def drop_automatic_responses(self):
        automatic_responses = ['Caso esta solicitação deva ser atendida de forma prioritária, favor ligar no ramal 324',
                               'Esta é uma resposta automática do sistema de ServiceDesk',
                               'Este chamado foi encerrado automaticamente',
                               'Sua solicitação será avaliada pela equipe responsável. Em breve você receberá um retorno']

        self.data = self.data[~self.data['COMMENT'].str.contains('|'.join(automatic_responses))].dropna()

    def drop_teams_messages(self):
        # Prevenindo o erro ao substituir NaN por string vazia
        self.data = self.data[~self.data['COMMENT'].str.contains('Você foi adicionado nas seguintes turmas')].dropna()

    def use_all_drops_methods(self):
        self.data['COMMENT'] = self.data['COMMENT'].fillna('')
        # self.drop_empty_comments()
        self.drop_automatic_responses()
        self.drop_teams_messages()

    def filter_by_first_message(self):
        # Filtrar apenas a primeira mensagem de cada ticket
        self.data = self.data.groupby('HD_TICKET_ID').first().reset_index()

    def generate_target(self):
        # Ordenar os dados por 'HD_TICKET_ID' e 'TIMESTAMP'
        self.order_by_HD_TICKET()

        # Capturar tickets únicos
        unique_tickets = self.data['HD_TICKET_ID'].unique()

        # Lista de regex que deseja verificar
        regex_patterns = [
            'Changed tíquete Fila from (.+?) to (.+?)\.',
            'Changed ticket Queue from (.+?) to (.+?)\.',
        ]

        # Iterar sobre cada ticket
        for ticket_id in unique_tickets:
            # Filtrar as linhas correspondentes ao ticket atual
            ticket_data = self.data[self.data['HD_TICKET_ID'] == ticket_id]

            # Variável para armazenar o resultado encontrado
            target_value = None

            # Procurar uma correspondência em cada descrição do ticket
            for index, row in ticket_data.iterrows():
                if isinstance(row['DESCRIPTION'], str):
                    cleaned_description = self.clean_description(row['DESCRIPTION'])

                    target_value = self.find_match_in_description(cleaned_description, regex_patterns)

                    if target_value:
                        break

            if target_value:
                first_index = ticket_data.index[0]
                self.data.at[first_index, 'TARGET'] = target_value
            else:
                first_index = ticket_data.index[0]
                self.data.at[first_index, 'TARGET'] = '1°Nível to SRI'

    def clean_description(self, description):
        """Remove quebras de linha e espaços extras da descrição."""
        return description.replace('\\n', '').strip()

    def find_match_in_description(self, description, patterns):
        """
        Verifica a descrição contra uma lista de padrões regex.
        Retorna o valor encontrado na primeira correspondência.
        """
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                if "Changed tíquete Fila" in pattern or "Changed ticket Queue" in pattern:
                    return match.group(2)
                else:
                    return match.group(0)
        return None



# Passando o caminho do arquivo JSON no momento de criar o objeto
start_time = time.time()
extractor = Extractor_v2("./data.json")
print(f"Carregamento de dados concluído em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.order_by_HD_TICKET()
print(f"Ordenação por HD_TICKET concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.drop_columns()
print(f"Remoção de colunas concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.fill_na()
print(f"Preenchimento de valores NA concluído em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.generate_target()
print(f"Geração de TARGET concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.filter_by_first_message()
print(f"Filtragem por primeira mensagem concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.use_all_drops_methods()
print(f"Aplicação de métodos de remoção concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.apply_comment_extraction()
print(f"Extração de comentários concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.show_data()
print(f"Exibição de dados concluída em {time.time() - start_time:.2f} segundos")

# Salvando o arquivo JSON
start_time = time.time()
extractor.save_data("./filtered_data.json")
print(f"Salvamento de dados concluído em {time.time() - start_time:.2f} segundos")
