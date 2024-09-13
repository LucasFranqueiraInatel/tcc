import json
from bs4 import BeautifulSoup


class Extractor:
    def __init__(self, path):
        self.path = path
        self.original_data = self.load_data()
        self.filtered_data = []
        self.discarded_data = []

    def load_data(self):
        # Carrega os dados do arquivo JSON
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_comment_text(self, comment_html):
        # Extrai o texto do HTML de comentários
        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            return soup.get_text()
        except Exception as e:
            return f"Erro ao extrair texto de COMMENT: {e}"
        
    def is_automatic_serviceDesk_response(self, comment_html):
        # Verifica se o comentário contém o texto da resposta automática
        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            comment_text = soup.get_text()
            if 'Caso esta solicitação deva ser atendida de forma prioritária, favor ligar no ramal 324' in comment_text or 'Esta é uma resposta automática do sistema de ServiceDesk' in comment_text:
                return True
            return False
        except Exception as e:
            return f"Erro ao verificar automatic_serviceDesk_response: {e}"

    def extract_data(self):
        for item in self.original_data:
            if isinstance(item, dict):
                if 'COMMENT' in item:
                    
                    comment_text = self.extract_comment_text(item['COMMENT'])

                    if self.is_automatic_serviceDesk_response(comment_text):
                        self.discarded_data.append(item)
                    else:
                        self.filtered_data.append(item)
                else:
                    self.filtered_data.append(item)
            else:
                print("Item não é um dicionário.")
            print(f'item {item['ID']}: processado.')

    def save_filtered_data(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.filtered_data, f, ensure_ascii=False, indent=4)

    def save_discarded_data(self, discarded_output_path):
        with open(discarded_output_path, 'w', encoding='utf-8') as f:
            json.dump(self.discarded_data, f, ensure_ascii=False, indent=4)

# Exemplo de uso
teste = Extractor('data.json')
teste.extract_data()  # Extrai os dados filtrados

# Salva os dados filtrados e os descartados em arquivos separados
teste.save_filtered_data('filtered_data.json')
teste.save_discarded_data('discarded_data.json')

print(teste.original_data.__len__())
print(teste.filtered_data.__len__())
print(teste.discarded_data.__len__())

