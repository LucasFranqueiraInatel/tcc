from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
from pipeline import treinar_e_salvar_modelos, carregar_modelos, classificar_em_cascata

# Dados de entrada
data = pd.read_json('./data/filtered_data.json')

# Vetorização dos comentários
vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), min_df=3)
X = vectorizer.fit_transform(data['COMMENT']).toarray()

# Codificação das classes
le = LabelEncoder()
y = le.fit_transform(data['TARGET'])
classes_originais = le.classes_  # Para reverter depois
print("Classes codificadas:", le.classes_)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinamento e salvamento dos modelos
#treinar_e_salvar_modelos(X_train, y_train, classes=classes_originais, pasta_modelos="meus_modelos")

# Classificação em cascata
modelos_carregados = carregar_modelos("meus_modelos")
ordem_classes = list(['ADM','CIDC', 'ICC', 'SRI', 'SSA', 'SSI', 'Suporte 1° Nível', 'Suporte 2° Nível'])  # Ordem desejada

resultados = classificar_em_cascata(modelos_carregados, X_test, ordem_classes)

# Ajustar 'Classe_Predita' para os valores inteiros correspondentes
resultados["Classe_Predita"] = resultados["Classe_Predita"].map(
    lambda x: le.transform([x])[0] if x in le.classes_ else -1  # Valor padrão para classes desconhecidas
)

# Remova possíveis valores inválidos (-1) do conjunto predito e teste correspondente
valid_indices = resultados["Classe_Predita"] != -1
resultados = resultados[valid_indices]
y_test = y_test[valid_indices]

print(classification_report(y_test, resultados['Classe_Predita'], target_names=classes_originais))
