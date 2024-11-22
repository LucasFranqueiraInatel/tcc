import os
import pickle
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

def treinar_e_salvar_modelos(X, y, classes, modelo_base=None, pasta_modelos="modelos"):
    """
    Treina e salva um modelo para cada classe.

    Parâmetros:
        X (array-like): Dados de entrada (vetorizados).
        y (array-like): Rótulos codificados.
        classes (list): Lista das classes originais.
        modelo_base (XGBClassifier): Modelo base para treinar.
        pasta_modelos (str): Diretório onde os modelos serão salvos.
    """
    os.makedirs(pasta_modelos, exist_ok=True)

    for i, classe in enumerate(classes):
        print(f"Treinando modelo para a classe '{classe}'...")
        
        # Criar labels binários
        y_bin = (y == i).astype(int)
        
        # Dividir os dados
        X_train, X_test, y_train, y_test = train_test_split(X, y_bin, stratify=y_bin, test_size=0.2, random_state=42)
        
        # Treinar modelo
        modelo = modelo_base or XGBClassifier(use_label_encoder=False, eval_metric="logloss")
        modelo.fit(X_train, y_train)
        
        # Salvar modelo
        nome_arquivo = os.path.join(pasta_modelos, f"xgboostClass_{classe}.pkl")
        with open(nome_arquivo, "wb") as f:
            pickle.dump(modelo, f)
        print(f"Modelo salvo: {nome_arquivo}")

def carregar_modelos(pasta_modelos):
    """
    Carrega todos os modelos salvos em uma pasta.
    """
    modelos = {}
    for arquivo in os.listdir(pasta_modelos):
        if arquivo.endswith(".pkl"):
            caminho = os.path.join(pasta_modelos, arquivo)
            with open(caminho, "rb") as f:
                modelo = pickle.load(f)
                modelos[arquivo.split("_")[-1].replace(".pkl", "")] = modelo
    return modelos

def classificar_em_cascata(modelos, X, ordem_classes):
    resultados = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
    resultados["Classe_Predita"] = None

    mascara_nao_classificada = np.ones(X.shape[0], dtype=bool)

    for classe in ordem_classes:
        if classe not in modelos:
            print(f"Atenção: Modelo '{classe}' não encontrado.")
            continue

        modelo = modelos[classe]
        y_pred = modelo.predict(X[mascara_nao_classificada])

        print(f"Predições para a classe '{classe}': {y_pred}")  # Verifique as predições

        indices_positivos = np.where(mascara_nao_classificada)[0][y_pred == 1]
        resultados.loc[indices_positivos, "Classe_Predita"] = classe
        mascara_nao_classificada[indices_positivos] = False

    return resultados

