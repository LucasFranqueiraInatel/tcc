from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import pandas as pd
import os
import pickle

# Carregando os dados
df = pd.read_json('./data/filtered_data.json')

# Ajustando a coluna TARGET para classes originais
df['TARGET'] = df['TARGET'].apply(lambda x: 'SSI' if x == 'SSI' else 'não SSI')

# Verificando as classes únicas
print("Classes únicas no TARGET:", df['TARGET'].unique())

# Vetorização de texto
vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=3)
X = vectorizer.fit_transform(df['COMMENT']).toarray()

# Codificação de rótulos
le = LabelEncoder()
y = le.fit_transform(df['TARGET'])  # Classes transformadas em números

# Divisão do conjunto com estratificação
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Treinamento com XGBoost
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Predições
y_pred = model.predict(X_test)

# Conversão de volta para as classes originais
y_test_labels = le.inverse_transform(y_test)
y_pred_labels = le.inverse_transform(y_pred)

# Avaliação
print("Acurácia:", accuracy_score(y_test_labels, y_pred_labels))
print("Relatório de Classificação:\n", classification_report(y_test_labels, y_pred_labels))

# pasta_modelos = "xgboostClassCascade"
# modelo_nome = "xgboostClass_SSI.pkl"

# # Criar o caminho completo do arquivo
# caminho_modelo = os.path.join(pasta_modelos, modelo_nome)

# nome_arquivo = os.path.join('./xgboostClassCascade', f"xgboostClass_SSI.pkl")
# with open(caminho_modelo, "wb") as f:
#     pickle.dump(model, f)

