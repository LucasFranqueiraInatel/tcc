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
        if comment_html is None:
            return ''  # Retorna string vazia se o comentário for None

        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            return soup.get_text()
        except Exception as e:
            return f"Erro ao extrair texto de COMMENT: {e}"

    def is_comment_empty(self, comment_html):
        # Verifica se o comentário está vazio
        if comment_html is None:
            return True  # Trata o None diretamente

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
            if 'Prezado, boa noite<br />Você foi adicionado nas seguintes turmas:<br /><strong>' in comment_text:
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
        for item in self.original_data:
            if isinstance(item, dict):
                if 'COMMENT' in item:
                    comment_html = item['COMMENT']

                    if self.is_comment_empty(comment_html) or self.is_automatic_serviceDesk_response(comment_html) or self.is_teams_message(comment_html):
                        self.discarded_data.append(item)
                    else:
                        self.filtered_data.append(item)
                else:
                    self.filtered_data.append(item)
            else:
                print("Item não é um dicionário.")
            # Certifique-se de que as aspas estão corretas
            print(f"Item {item['ID']}: processado.")

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

print(f"Total de dados originais: {len(teste.original_data)}")
print(f"Total de dados filtrados: {len(teste.filtered_data)}")
print(f"Total de dados descartados: {len(teste.discarded_data)}")
