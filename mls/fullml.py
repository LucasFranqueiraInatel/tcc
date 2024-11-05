import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import StratifiedKFold

df = pd.read_json('./data/filtered_data.json')

# Separando as variáveis
X = df['COMMENT']
y = df['TARGET']

# Convertendo o texto em vetores TF-IDF
tfidf = TfidfVectorizer()
X_tfidf = tfidf.fit_transform(X)

# Dividindo os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Configurando o XGBoost com regularização
xgb_clf = XGBClassifier(
    use_label_encoder=False,
    eval_metric='logloss',
)

# Criando o modelo One-vs-Rest
ovr_model = OneVsRestClassifier(xgb_clf)

# Usando validação cruzada (StratifiedKFold) para avaliar o modelo
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(ovr_model, X_train, y_train, cv=cv, scoring='accuracy')

# Treinando o modelo com todo o conjunto de treino
ovr_model.fit(X_train, y_train)

# Fazendo previsões no conjunto de teste
y_pred = ovr_model.predict(X_test)

# Exibindo os resultados
print("Cross-Validation Accuracy Scores:", cv_scores)
print("Mean Cross-Validation Accuracy:", cv_scores.mean())
print("\nTest Set Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
