import pandas as pd

class Extractor_v2:

    def __init__(self):
        # self.data = self.load_data(path)
        pass

    def load_data(self, path):
        self.data = pd.read_json(path)

    def order_by_HD_TICKET(self):
        self.data = self.data.sort_values(by=["HD_TICKET_ID"])

    def drop_columns(self):
        self.data = self.data.drop(columns=['COMMENT_LOC', 'DESCRIPTION', 'OWNERS_ONLY_DESCRIPTION', 'LOCALIZED_DESCRIPTION', 'LOCALIZED_OWNERS_ONLY_DESCRIPTION', 'MAILED', 'MAILED_TIMESTAMP', 'MAILER_SESSION', 'NOTIFY_USERS', 'VIA_EMAIL', 'OWNERS_ONLY', 'RESOLUTION_CHANGED', 'SYSTEM_COMMENT', 'TICKET_DATA_CHANGE', 'VIA_SCHEDULED_PROCESS', 'VIA_IMPORT', 'VIA_BULK_UPDATE'])

    def show_data(self):
        print(self.data)

extractor = Extractor_v2()
extractor.load_data("./data.json")
extractor.order_by_HD_TICKET()
extractor.drop_columns()
extractor.show_data()
