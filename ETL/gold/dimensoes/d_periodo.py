import pandas as pd
import hashlib

# -----------------------------------------------------------
# Script de Criação da Dimensão PERÍODO
# Autor:
# Data de Criação:
# Descrição: Este script lê dados de um arquivo CSV, gera períodos
# a partir do ano mínimo e máximo dos períodos de ingresso na UFRJ,
# cria uma chave substituta (sk_d_periodo) para cada período usando
# SHA-256 e salva o resultado em um novo arquivo CSV.
# -----------------------------------------------------------


def gerar_periodos(df):
    """
    Gera uma lista de períodos entre o ano mínimo e máximo encontrados
    na coluna 'periodo_ingresso_ufrj' do DataFrame.

    Args:
        df (DataFrame): DataFrame contendo a coluna 'periodo_ingresso_ufrj'.

    Returns:
        DataFrame: DataFrame com os períodos gerados.
    """
    min_periodo = int(df["periodo_ingresso_ufrj"].min().split("/")[0])
    max_periodo = int(df["periodo_ingresso_ufrj"].max().split("/")[0])

    anos = range(min_periodo, max_periodo + 1)
    semestres = [0, 1, 2, 3]

    data = [
        [ano, semestre, f"{ano}/{semestre}"] for ano in anos for semestre in semestres
    ]

    return pd.DataFrame(data, columns=["ano", "semestre", "periodo"])


# Caminho para o diretório de dados
data_path = "../../../database"

# Leitura do arquivo CSV
df = pd.read_csv(f"{data_path}/silver/arquivo_anonimizado_v2.csv")

# Colunas da dimensão PERÍODO
colunas_periodo = ["sk_d_periodo", "ano", "semestre", "periodo"]

# Geração dos períodos
d_periodo = gerar_periodos(df)

# Criação do sk_d_periodo usando SHA-256
d_periodo["sk_d_periodo"] = d_periodo.apply(
    lambda x: hashlib.sha256(str(x["periodo"]).encode()).hexdigest(), axis=1
)

# Reordenação das colunas
d_periodo = d_periodo.reindex(columns=colunas_periodo)

# Salvamento do DataFrame resultante em CSV
d_periodo.to_csv(f"{data_path}/gold/d_periodo.csv", index=False)
