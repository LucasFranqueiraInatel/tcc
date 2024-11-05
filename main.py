from extractor import Extractor_v2
from db.mongo_connect import Database
import time

start_time = time.time()
extractor = Extractor_v2('./data/data.json')
# extractor = Extractor_v2('data/data.json')
print(f"Carregamento de dados concluído em {time.time() - start_time:.2f} segundos")
print('Quantidade de registros:', len(extractor.data))

start_time = time.time()
extractor.order_by_HD_TICKET()
print(f"Ordenação por HD_TICKET concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.fill_na()
print(f"Preenchimento de valores NA concluído em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.remove_befora_data("2015-01-01")
print(f"Remoção de dados anteriores a 2023 concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.generate_target()
print(f"Geração de TARGET concluída em {time.time() - start_time:.2f} segundos")

# start_time = time.time()
# extractor.filter_by_first_message()
# print(f"Filtragem por primeira mensagem concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.use_all_drops_methods()
print(f"Aplicação de métodos de remoção concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.apply_comment_extraction()
print(f"Extração de comentários concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.drop_columns()
print(f"Remoção de colunas concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.show_data()
print(f"Exibição de dados concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.clean_text_column('COMMENT')
print(f"Remoção de tabs e espacos concluída em {time.time() - start_time:.2f} segundos")

start_time = time.time()
extractor.save_data("data/filtered_data.json")
print(f"Salvamento de dados concluído em {time.time() - start_time:.2f} segundos")
