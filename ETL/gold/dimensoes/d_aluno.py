import pandas as pd
import hashlib

# -----------------------------------------------------------
# Script de Criação da Dimensão ALUNO
# Autor: Marcos Eduardo
# Data de Criação: 2024-07-04
# Descrição: Este script lê dados de um arquivo CSV, remove duplicatas,
# gera uma chave substituta (sk_d_aluno) para cada aluno usando SHA-256
# e salva o resultado em um novo arquivo CSV.
# -----------------------------------------------------------

# Caminho para o diretório de dados
data_path = "../../../database"

# Leitura do arquivo CSV
df = pd.read_csv(f"{data_path}/silver/arquivo_anonimizado_v2.csv")

# Colunas da dimensão ALUNO
colunas_aluno = [
    "sk_d_aluno",
    "nome_completo",
    "matricula_dre",
    "sexo",
    "idade",
    "data_nascimento",
    "periodo_ingresso_curso_atual",
    "periodo_ingresso_ufrj",
    "forma_ingresso",
    "modalidade_cota",
    "nota_enem",
]

# Seleção e remoção de duplicatas
d_aluno = df[colunas_aluno[1:]].drop_duplicates().reset_index(drop=True)

# Criação do sk_d_aluno usando SHA-256
d_aluno["sk_d_aluno"] = d_aluno["matricula_dre"].apply(
    lambda matricula: hashlib.sha256(matricula.encode()).hexdigest()
)

# Reordenação das colunas
d_aluno = d_aluno[["sk_d_aluno"] + colunas_aluno[1:]]

# Salvamento do DataFrame resultante em CSV
d_aluno.to_csv(f"{data_path}/gold/d_aluno.csv", index=False)
