import pandas as pd
import hashlib
import numpy as np

# -----------------------------------------------------------
# Script de Criação da Dimensão DISCIPLINA
# Autor:
# Data de Criação:
# Descrição: Este script lê dados de um arquivo CSV, processa a coluna
# 'disciplinas_cursadas' para separar os detalhes das disciplinas,
# gera uma chave substituta (sk_d_disciplina) para cada disciplina usando
# SHA-256 e salva o resultado em um novo arquivo CSV.
# -----------------------------------------------------------


def processar_disciplina(disciplina):
    """
    Processa uma string de detalhes de disciplina, dividindo em componentes.

    Args:
        disciplina (str): String contendo os detalhes da disciplina.

    Returns:
        tuple: Uma tupla contendo os detalhes processados da disciplina.
    """
    detalhes_disciplinas = disciplina.split(" - ")
    if len(detalhes_disciplinas) == 5:
        detalhes_disciplinas[1] = " - ".join(detalhes_disciplinas[1:3])
        del detalhes_disciplinas[2]
    return tuple(detalhes_disciplinas)


def obter_disciplina_e_codigo(x):
    """
    Extrai código e nome da disciplina a partir de uma lista de strings.

    Args:
        x (list): Lista contendo os detalhes da disciplina.

    Returns:
        tuple: Uma tupla com o código e o nome da disciplina, ou NaN se não disponível.
    """
    if x[0] == "nan":
        return np.nan
    try:
        return (
            x[1].split()[0].replace(" ", ""),
            " ".join(x[1].split()[1:]),
        )
    except IndexError:
        print("Erro de índice para:", x)
        return None


# Caminho para o diretório de dados
data_path = "../../../database"

# Leitura do arquivo CSV
df = pd.read_csv(f"{data_path}/silver/arquivo_anonimizado_v2.csv")

# Converte a coluna 'disciplinas_cursadas' para string
df["disciplinas_cursadas"] = df["disciplinas_cursadas"].astype(str)

# Processa a coluna 'disciplinas_cursadas' para separar em periodo, disciplina, grau, situação
df["disciplinas_cursadas"] = df["disciplinas_cursadas"].apply(
    lambda row: [processar_disciplina(item) for item in row.split("\n")]
)

# Explode a coluna 'disciplinas_cursadas' para dividir as listas em linhas separadas
df_exploded = df.explode("disciplinas_cursadas")

# Processa os detalhes das disciplinas
df_exploded["disciplinas_cursadas"] = df_exploded["disciplinas_cursadas"].apply(
    obter_disciplina_e_codigo
)

# Remove linhas com valores NaN
df_exploded.dropna(inplace=True)

# Cria DataFrame da dimensão DISCIPLINA
df_disciplina = pd.DataFrame(
    df_exploded["disciplinas_cursadas"].tolist(),
    index=df_exploded.index,
    columns=["cod_disciplina", "nome_disciplina"],
)

# Remove duplicatas
d_disciplina = df_disciplina.drop_duplicates().reset_index(drop=True)

# Criação do sk_d_disciplina usando SHA-256
d_disciplina["sk_d_disciplina"] = d_disciplina.apply(
    lambda x: hashlib.sha256(
        str(x["cod_disciplina"] + x["nome_disciplina"]).encode()
    ).hexdigest(),
    axis=1,
)

# Reordenação das colunas
colunas_disciplina = ["sk_d_disciplina", "cod_disciplina", "nome_disciplina"]
d_disciplina = d_disciplina.reindex(columns=colunas_disciplina)

# Salvamento do DataFrame resultante em CSV
d_disciplina.to_csv(f"{data_path}/gold/d_disciplina.csv", index=False)
