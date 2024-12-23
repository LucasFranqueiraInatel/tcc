import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time
import re
import json


class Extractor_v2:

    def __init__(self, path):
        if isinstance(path, str):
            self.data = self.load_data(path)
        elif isinstance(path, pd.DataFrame):
            self.data = path

    def load_data(self, path):
        return pd.read_json(path)

    def show_data(self):
        print(self.data)

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
            columns=['OWNERS_ONLY_DESCRIPTION', 'COMMENT_LOC', 'LOCALIZED_DESCRIPTION',
                     'LOCALIZED_OWNERS_ONLY_DESCRIPTION', 'MAILED', 'MAILED_TIMESTAMP', 'MAILER_SESSION',
                     'NOTIFY_USERS', 'VIA_EMAIL', 'OWNERS_ONLY', 'RESOLUTION_CHANGED', 'SYSTEM_COMMENT',
                     'TICKET_DATA_CHANGE', 'VIA_SCHEDULED_PROCESS', 'VIA_IMPORT', 'VIA_BULK_UPDATE'])

    def fill_na(self):
        self.data = self.data.fillna(np.nan)

    @staticmethod
    def extract_comment_text(comment_html):
        """
        Extrai o texto puro de um conteúdo HTML usando BeautifulSoup,
        se necessário. Caso contrário, retorna o texto bruto.
        """
        if comment_html is None:
            return ''
        if isinstance(comment_html, str) and (
                comment_html.strip().startswith('<') or comment_html.strip().startswith('&lt;')):
            # Verifica se parece ser HTML
            try:
                soup = BeautifulSoup(comment_html, 'html.parser')
                return soup.get_text()
            except Exception as e:
                return f"Erro ao extrair texto de COMMENT: {e}"
        else:
            # Caso contrário, retorna o texto bruto
            return comment_html

    @staticmethod
    def removing_useless_text(comment):
        """
        Remove padrões indesejados do texto, como avisos ou formatos irrelevantes.
        """
        if comment is None:
            return ''

        # Lista de padrões indesejados para remover
        patterns = [
            r'ATENÇÃO: Este email veio de um remetente externo. Não siga instruções, clique em links ou abra anexos a não ser que você reconheça o remetente e saiba que o conteúdo é seguro. ',
            r'Some people who received this message.*?Learn why this is important',
            r'[-]{2,}',
            r'[#]{2,}',
            r'\s{2,}',
            r'<table[^>]*>',
            r'</table>',
            r'<tbody[^>]*>',
            r'</tbody>',
            r'<tr[^>]*>',
            r'</tr>',
            r'<td[^>]*>',
            r'</td>',
        ]

        if isinstance(comment, str):
            for pattern in patterns:
                comment = re.sub(pattern, '', comment, flags=re.IGNORECASE)

        return comment.strip()

    def apply_comment_extraction(self):
        """
        Aplica a extração de texto de HTML e remove padrões inúteis em série.
        """
        self.data['COMMENT'] = (
            self.data['COMMENT']
            .apply(self.extract_comment_text)
            .apply(self.removing_useless_text)
        )

    def drop_useless_message(self):
        self.data = self.data[~((self.data['COMMENT'] == '') & (self.data['DESCRIPTION'] == ''))].dropna()

    def drop_automatic_responses(self):
        automatic_responses = ['Caso esta solicitação deva ser atendida de forma prioritária, favor ligar no ramal 324',
                               'Esta é uma resposta automática do sistema de ServiceDesk',
                               'Este chamado foi encerrado automaticamente',
                               'Sua solicitação será avaliada pela equipe responsável. Em breve você receberá um retorno',
                               'Review These Messages1 messages are being held for you to review as of']

        self.data = self.data[~self.data['COMMENT'].str.contains('|'.join(automatic_responses))].dropna()

    def drop_teams_messages(self):
        # Prevenindo o erro ao substituir NaN por string vazia
        self.data = self.data[~self.data['COMMENT'].str.contains('Você foi adicionado nas seguintes turmas')].dropna()

    def drop_deleted_comments(self):
        # Define o padrão regex para identificar as mensagens de usuário ou dispositivo excluídos
        pattern = r'User ".*?" was deleted|Device ".*?" was deleted'

        # Filtra o DataFrame para manter apenas as linhas que não correspondem ao padrão
        self.data = self.data[~self.data['COMMENT'].str.contains(pattern, na=False, regex=True)]

    def drop_comments_with_no_text(self):
        self.data = self.data[self.data['COMMENT'].str.strip() != '']

    def use_all_drops_methods(self):
        self.data['COMMENT'] = self.data['COMMENT'].fillna('')
        self.drop_automatic_responses()
        self.drop_teams_messages()
        self.drop_useless_message()
        self.drop_deleted_comments()
        self.drop_comments_with_no_text()

    def filter_by_first_message(self):
        # Filtrar apenas a primeira mensagem de cada ticket
        self.data = self.data.groupby('HD_TICKET_ID').first().reset_index()

    def remove_befora_data(self, date):
        self.data = self.data[self.data['TIMESTAMP'] > date]

    def generate_target(self):
        mapping = {
            'SUPORTE - 1°Nível': 'Suporte 1° Nível',
            'Suporte-1°Nível': 'Suporte 1° Nível',
            'SSA - 2° Nível': 'SSA',
            'SRI - 2°Nível': 'SRI',
            'Suporte ICC-2° Nível': 'ICC',
            'Suporte Geral-2° Nível': 'Suporte 2° Nível',
            'ADM': 'ADM',
            'Suporte Geral - 2°Nível - HUAWEI': 'CIDC',
            'Suporte Geral - 2°Nível - CIDC': 'CIDC',
            'Segurança': 'SSI',
            'SSI - 2°Nível': 'SSI',
            'Empréstimo ': 'Empréstimo',
            'SUPORTE - 2°Nível': 'Suporte 2° Nível',
            'SUP - 2°Nível': 'Suporte 2° Nível',
            'ICC - 2°Nível': 'ICC',
            'CIDC - 2°Nivel': 'CIDC',
            'SSA - 2°Nível': 'SSA',
            'SUPORTE CIDC - 2°Nivel': 'CIDC',
            'SUPORTE ICC - 2° Nível': 'ICC',
            'Pendências': 'Pendências',
            'Projetos da SRI': 'SRI'
        }

        # Ordenar os dados por 'HD_TICKET_ID' e 'TIMESTAMP'
        self.order_by_HD_TICKET()

        # Capturar tickets únicos
        unique_tickets = self.data['HD_TICKET_ID'].unique()

        # Lista de regex que deseja verificar
        regex_patterns = [
            r'Changed tíquete Fila from (.+?) to (.+?)\.',
            r'Changed ticket Queue from (.+?) to (.+?)\.'
        ]

        # Iterar sobre cada ticket
        for ticket_id in unique_tickets:
            # Filtrar as linhas correspondentes ao ticket atual
            ticket_data = self.data[self.data['HD_TICKET_ID'] == ticket_id]

            # Flag para detectar se houve mudança de fila
            has_queue_change = False

            # Verificar se há mudanças de fila ao longo do ticket
            for _, row in ticket_data.iterrows():
                if isinstance(row['DESCRIPTION'], str):
                    cleaned_description = self.clean_description(row['DESCRIPTION'])
                    if self.find_match_in_description(cleaned_description, regex_patterns):
                        has_queue_change = True
                        break

            # Somente definir "Suporte 1° Nível" se nenhuma mudança de fila foi encontrada
            if not has_queue_change:
                # Aplicar "Suporte 1° Nível" para todas as mensagens se não houve nenhuma mudança
                self.data.loc[ticket_data.index, 'TARGET'] = 'Suporte 1° Nível'
                continue  # Ir para o próximo ticket

            # Segunda passagem: aplicar targets com base nas mudanças detectadas
            current_target = None
            for index, row in ticket_data.iterrows():
                if isinstance(row['DESCRIPTION'], str):
                    cleaned_description = self.clean_description(row['DESCRIPTION'])
                    new_target = self.find_match_in_description(cleaned_description, regex_patterns)

                    if new_target:
                        new_target = mapping.get(new_target, new_target)
                        current_target = new_target

                    # Aplicar o target atual à linha atual, se encontrado
                    if current_target:
                        self.data.at[index, 'TARGET'] = current_target

        # Remover linhas com targets indesejados
        self.data = self.data[~self.data['TARGET'].isin(['Pendências', 'Empréstimo'])]

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

    def clean_text_column(self, column_name):
        # Replace newlines and tabs with a space
        self.data[column_name] = self.data[column_name].str.replace('\n', ' ', regex=True)
        self.data[column_name] = self.data[column_name].str.replace('\t', ' ', regex=True)
        self.data[column_name] = self.data[column_name].str.replace('&nbsp;', ' ', regex=True)
        self.data[column_name] = self.data[column_name].str.replace('\n;', ' ', regex=True)
        self.data[column_name] = self.data[column_name].str.replace('\r', ' ', regex=True)
        self.data[column_name] = self.data[column_name].str.replace(' ', ' ', regex=True)
        self.data[column_name] = self.data[column_name].str.replace('<br />', ' ', regex=True)

        # Optionally, remove extra spaces that may result from the replacements
        self.data[column_name] = self.data[column_name].str.replace(' +', ' ', regex=True).str.strip()

    def return_data(self):
        return self.data