import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time

class Extractor_v2:

    def __init__(self, path):
        self.data = self.load_data(path)

    def load_data(self, path):
        return pd.read_json(path)  # Corrigido: agora retorna o DataFrame

    def order_by_HD_TICKET(self):
        self.data = self.data.sort_values(by=["HD_TICKET_ID", "TIMESTAMP"])

    def drop_columns(self):
        self.data = self.data.drop(
            columns=['COMMENT_LOC', 'OWNERS_ONLY_DESCRIPTION', 'LOCALIZED_DESCRIPTION',
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
        # Prevenindo o erro ao substituir NaN por string vazia
        self.data = self.data[~self.data['COMMENT'].str.contains('|'.join(automatic_responses))].dropna()

    def drop_teams_messages(self):
        # Prevenindo o erro ao substituir NaN por string vazia
        self.data = self.data[~self.data['COMMENT'].str.contains('Você foi adicionado nas seguintes turmas')].dropna()

    def use_all_drops_methods(self):
        self.data['COMMENT'] = self.data['COMMENT'].fillna('')
        # self.drop_empty_comments()
        self.drop_automatic_responses()
        self.drop_teams_messages()




# Passando o caminho do arquivo JSON no momento de criar o objeto
start_time = time.time()
extractor = Extractor_v2("./data.json")
print(f"Carregamento de dados concluído em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.order_by_HD_TICKET()
print(f"Ordenação por HD_TICKET concluída em {time.time() - start_time:.2f} segundos")

# start_time = time.time()
# extractor.drop_columns()
# print(f"Remoção de colunas concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.fill_na()
print(f"Preenchimento de valores NA concluído em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.apply_comment_extraction()
print(f"Extração de comentários concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.use_all_drops_methods()
print(f"Aplicação de métodos de remoção concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.show_data()
print(f"Exibição de dados concluída em {time.time() - start_time:.2f} segundos")
