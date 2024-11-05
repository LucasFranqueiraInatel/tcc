from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

df = pd.read_json('./data/filtered_data.json')

df['TARGET'] = df['TARGET'].apply(lambda x: 1 if x == 'Suporte 1° Nível' else 0)

print(df['TARGET'].unique())

# Vetorização de texto
vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=3)
X = vectorizer.fit_transform(df['COMMENT']).toarray()

# Codificação de rótulos
le = LabelEncoder()
y = le.fit_transform(df['TARGET'])

# Divisão do conjunto com estratificação
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Treinamento com XGBoost e balanceamento
model = XGBClassifier(
    n_estimators=300,
    max_depth=7,
    learning_rate=0.1,
    random_state=42
)
model.fit(X_train, y_train)

# Predições
y_pred = model.predict(X_test)

# Avaliação e conversão de volta para classes originais
y_test_labels = le.inverse_transform(y_test)
y_pred_labels = le.inverse_transform(y_pred)

print("Acurácia:", accuracy_score(y_test_labels, y_pred_labels))
print(classification_report(y_test_labels, y_pred_labels))