import json
from bs4 import BeautifulSoup


class Extractor:
    def __init__(self, path):
        self.path = path
        self.original_data = self.load_data()
        self.filtered_data = []
        self.discarded_data = []
        self.useds_ids = []

    def load_data(self):
        # Carrega os dados do arquivo JSON
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_comment_text(self, comment_html):
        # Extrai o texto do HTML de comentários
        if comment_html is None:
            return ''

        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            return soup.get_text()
        except Exception as e:
            return f"Erro ao extrair texto de COMMENT: {e}"
        
    def isnt_first_message(self, id):
        # Verifica se o comentário é o primeiro da conversa
        try:
            if id in self.useds_ids:
                return True
            else:
                self.useds_ids.append(id)
                return False
        except Exception as e:
            return f"Erro ao verificar se COMMENT é o primeiro da conversa: {e}"

    def is_comment_empty(self, comment_html):
        # Verifica se o comentário está vazio
        if comment_html is None:
            return True 

        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            comment_text = soup.get_text()
            if comment_text.strip() == '' or comment_text.strip() == '\n' or comment_text.strip() == '\n\n':
                return True
            return False
        except Exception as e:
            return f"Erro ao verificar se COMMENT está vazio: {e}"

    def is_teams_message(self, comment_html):
        # Verifica se o comentário é uma mensagem do Teams
        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            comment_text = soup.get_text()
            if 'Você foi adicionado nas seguintes turmas' in comment_text:
                return True
            return False
        except Exception as e:
            return f"Erro ao verificar se COMMENT é uma mensagem do Teams: {e}"

    def is_automatic_serviceDesk_response(self, comment_html):
        # Verifica se o comentário contém o texto da resposta automática
        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            comment_text = soup.get_text()
            if 'Caso esta solicitação deva ser atendida de forma prioritária, favor ligar no ramal 324' in comment_text or 'Esta é uma resposta automática do sistema de ServiceDesk' in comment_text or 'Este chamado foi encerrado automaticamente' in comment_text or 'Sua solicitação será avaliada pela equipe responsável. Em breve você receberá um retorno' in comment_text:
                return True
            return False
        except Exception as e:
            return f"Erro ao verificar automatic_serviceDesk_response: {e}"

    def extract_data(self):
        keys_to_remove = ['COMMENT_LOC', 'DESCRIPTION', 'OWNERS_ONLY_DESCRIPTION', 'LOCALIZED_DESCRIPTION', 'LOCALIZED_OWNERS_ONLY_DESCRIPTION', 'MAILED', 'MAILED_TIMESTAMP', 'MAILER_SESSION', 'NOTIFY_USERS', 'VIA_EMAIL', 'OWNERS_ONLY', 'RESOLUTION_CHANGED', 'SYSTEM_COMMENT', 'TICKET_DATA_CHANGE', 'VIA_SCHEDULED_PROCESS', 'VIA_IMPORT', 'VIA_BULK_UPDATE']

        for item in self.original_data:
            if isinstance(item, dict):
                if 'COMMENT' in item and 'HD_TICKET_ID' in item:
                    comment_html = item['COMMENT']
                    
                    # Limpa o HTML do COMMENT
                    clean_comment = self.extract_comment_text(comment_html)
                    item['COMMENT'] = clean_comment

                    if self.is_comment_empty(clean_comment) or self.is_automatic_serviceDesk_response(clean_comment) or self.is_teams_message(clean_comment) or self.isnt_first_message(item['HD_TICKET_ID']):
                        self.discarded_data.append(item)
                    else:
                        for key in keys_to_remove:
                            item.pop(key, None)
                        self.filtered_data.append(item)
                else:
                    self.filtered_data.append(item)
            else:
                print("Item não é um dicionário.")
            print(f"Item {item['ID']}: processado.")

    def save_filtered_data(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.filtered_data, f, ensure_ascii=False, indent=4)

    def save_discarded_data(self, discarded_output_path):
        with open(discarded_output_path, 'w', encoding='utf-8') as f:
            json.dump(self.discarded_data, f, ensure_ascii=False, indent=4)


# Exemplo de uso
teste = Extractor('data.json')
teste.extract_data()

teste.save_filtered_data('filtered_data.json')
teste.save_discarded_data('discarded_data.json')

print(f"Total de dados originais: {len(teste.original_data)}")
print(f"Total de dados filtrados: {len(teste.filtered_data)}")
print(f"Total de dados descartados: {len(teste.discarded_data)}")
