import spacy
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

# Carregar o arquivo JSON
data = pd.read_json('../data/filtered_data.json')
df = pd.DataFrame(data)

# Carregar o modelo do spaCy para português
nlp = spacy.load('pt_core_news_sm')

# Função para limpar texto
def limpar_texto(texto):
    texto = re.sub(r"http\S+|www\S+|mailto\S+|[\[\](){}:;.,]", '', texto)  # Remove URLs e caracteres especiais
    texto = texto.lower()  # Converte para minúsculas
    doc = nlp(texto)  # Processa o texto com spaCy
    tokens = [token.lemma_ for token in doc if not token.is_stop]  # Lematiza e remove stopwords
    return ' '.join(tokens)

# Aplicar a função de limpeza ao campo 'COMMENT'
df['COMMENT'] = df['COMMENT'].apply(limpar_texto)

# Vetorização e modelo
vectorizer = TfidfVectorizer(max_features=3000)
X = vectorizer.fit_transform(df['COMMENT']).toarray()  # Vetorizar os comentários
y = df['TARGET']  # Variável alvo

# Divisão dos dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=20)

# Modelo Naive Bayes
model = MultinomialNB()
model.fit(X_train, y_train)

# Fazer previsões
y_pred = model.predict(X_test)

# Avaliar o modelo
print("Acurácia:", accuracy_score(y_test, y_pred))
print("Relatório de Classificação:\n", classification_report(y_test, y_pred))
