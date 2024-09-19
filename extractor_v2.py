import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

class Extractor_v2:

    def __init__(self):
        # self.data = self.load_data(path)
        pass

    def load_data(self, path):
        self.data = pd.read_json(path)

    def order_by_HD_TICKET(self):
        self.data = self.data.sort_values(by=["HD_TICKET_ID"])

    def drop_columns(self):
        self.data = self.data.drop(
            columns=['COMMENT_LOC', 'DESCRIPTION', 'OWNERS_ONLY_DESCRIPTION', 'LOCALIZED_DESCRIPTION',
                     'LOCALIZED_OWNERS_ONLY_DESCRIPTION', 'MAILED', 'MAILED_TIMESTAMP', 'MAILER_SESSION',
                     'NOTIFY_USERS', 'VIA_EMAIL', 'OWNERS_ONLY', 'RESOLUTION_CHANGED', 'SYSTEM_COMMENT',
                     'TICKET_DATA_CHANGE', 'VIA_SCHEDULED_PROCESS', 'VIA_IMPORT', 'VIA_BULK_UPDATE'])

    def fill_na(self):
        self.data = self.data.fillna(np.nan)

    @staticmethod
    def extract_comment_text(comment_html):
        if comment_html is None:
            return ''
        try:
            soup = BeautifulSoup(comment_html, 'html.parser')
            return soup.get_text()
        except Exception as e:
            return f"Erro ao extrair texto de COMMENT: {e}"

    def show_data(self):
        print(self.data)

    def apply_comment_extraction(self):
        self.data['COMMENT'] = self.data['COMMENT'].apply(self.extract_comment_text)


extractor = Extractor_v2()
extractor.load_data("./data.json")
extractor.order_by_HD_TICKET()
extractor.drop_columns()
extractor.fill_na()
extractor.apply_comment_extraction()
extractor.show_data()
