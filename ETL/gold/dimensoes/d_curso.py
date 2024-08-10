import pandas as pd
import hashlib

# -----------------------------------------------------------
# Script de Criação da Dimensão CURSO
# Autor: Marcos
# Data de Criação:  2024-07-04
# Descrição: Este script lê dados de um arquivo CSV, remove duplicatas,
# gera uma chave substituta (sk_d_curso) para cada curso usando SHA-256
# e salva o resultado em um novo arquivo CSV.
# -----------------------------------------------------------

# Caminho para o diretório de dados
data_path = "../../../database"

# Leitura do arquivo CSV
df = pd.read_csv(f"{data_path}/silver/arquivo_anonimizado_v2.csv")

# Colunas da dimensão CURSO
colunas_curso = [
    "sk_d_curso",
    "cod_curso_ingresso",
    "curso_ingresso_ufrj",
    "cod_curso_atual",
    "curso_atual",
]

# Seleção e remoção de duplicatas
d_curso = df[colunas_curso[1:]].drop_duplicates().reset_index(drop=True)

# Criação do sk_d_curso usando SHA-256
d_curso["sk_d_curso"] = d_curso.apply(
    lambda x: hashlib.sha256(
        str(x["cod_curso_ingresso"] + x["cod_curso_atual"]).encode()
    ).hexdigest(),
    axis=1,
)

# Reordenação das colunas
d_curso = d_curso[["sk_d_curso"] + colunas_curso[1:]]

# Salvamento do DataFrame resultante em CSV
d_curso.to_csv(f"{data_path}/gold/d_curso.csv", index=False)
