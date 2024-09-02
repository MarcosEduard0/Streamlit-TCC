import pandas as pd
import streamlit as st
import pandas as pd
from typing import List, Union
from utils.configs.parameters import gerar_caminho_database


def extrair_dados_database(nome_arquivo, camada):
    caminho_arquivo = gerar_caminho_database(nome_arquivo, camada)
    return pd.read_parquet(caminho_arquivo)


@st.cache_data
def carregar_dados(datasets=None):
    """
    Carrega os dados dos arquivos Parquet especificados pelo usuário.

    Args:
        datasets (list, optional): Lista de nomes dos datasets a serem carregados.
                                   Se None, todos os datasets serão carregados.

    Returns:
        dict: Dicionário onde as chaves são os nomes dos datasets e os valores são os DataFrames carregados.
    """
    # Dicionário mapeando nomes de datasets para os respectivos arquivos Parquet
    arquivos_parquet = {
        "d_periodo": "d_periodo.parquet",
        "d_aluno": "d_aluno.parquet",
        "d_disciplina": "d_disciplina.parquet",
        "d_curso": "d_curso.parquet",
        "d_situacao": "d_situacao.parquet",
        "f_matricula_aluno": "f_situacao_metricula.parquet",
        "f_situacao_periodo": "f_situacao_periodo.parquet",
        "f_desempenho_academico": "f_desempenho_academico.parquet",
    }

    # Se nenhum dataset for especificado, carregar todos
    if datasets is None:
        datasets = arquivos_parquet.keys()

    dados_carregados = {}
    for dataset in datasets:
        if dataset in arquivos_parquet:
            dados_carregados[dataset] = extrair_dados_database(
                arquivos_parquet[dataset], "gold"
            )

    # Calcula o período atual se 'd_aluno' foi carregado
    if "d_aluno" in dados_carregados:
        dados_carregados["periodo_atual"] = dados_carregados[
            "d_aluno"
        ].DS_PERIODO_INGRESSO_UFRJ.max()

    return dados_carregados


def calcular_periodo(periodo: str, delta: int) -> str:
    ano, semestre = map(int, periodo.split("/"))

    # Ajustar o semestre
    novo_semestre = semestre + delta

    # Ajustar o ano conforme necessário
    while novo_semestre < 1:
        ano -= 1
        novo_semestre += 2

    while novo_semestre > 2:
        ano += 1
        novo_semestre -= 2

    return f"{ano}/{novo_semestre}"


def merge_dataframes(
    dimensions: List[pd.DataFrame], fact: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge multiple dimension dataframes with a fact dataframe.

    Parameters:
    dimensions (list): List of dimension dataframes.
    fact (DataFrame): The fact dataframe to be merged with dimensions.
    keys (list): List of keys to merge on for each dimension.

    Returns:
    DataFrame: The merged dataframe.
    """
    merged_df = fact
    for dimension in dimensions:
        merged_df = pd.merge(merged_df, dimension)

    return merged_df


def merge_dataframes2(
    dimensions: List[pd.DataFrame], fact: pd.DataFrame, keys: Union[List[str], str]
) -> pd.DataFrame:
    """
    Merge multiple dimension dataframes with a fact dataframe.

    Parameters:
    dimensions (list): List of dimension dataframes.
    fact (DataFrame): The fact dataframe to be merged with dimensions.
    keys (list): List of keys to merge on for each dimension.

    Returns:
    DataFrame: The merged dataframe.
    """
    merged_df = fact
    for dimension, key in zip(dimensions, keys):
        merged_df = pd.merge(merged_df, dimension, on=key, how="inner")

    # Remove merge keys from the final dataframe
    merged_df.drop(keys, inplace=True, axis=1)

    return merged_df
