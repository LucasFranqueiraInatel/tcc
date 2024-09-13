import re
import unicodedata

text = '\nPrezado(a) Aline do Couto Pereira Vieira .\n\nEsta é uma resposta automática do sistema de ServiceDesk.\nUma observação foi adicionada em seu chamado.\n\nStatus do Chamado:  \nAberto\n\nChamado Registrado para: \nSSA - 2º Nível\n\nChamado Número : \n1011452\n\nObrigado.\n'
updated_text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')


print(updated_text)