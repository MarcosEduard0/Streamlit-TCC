import pandas as pd
import streamlit as st
import pandas as pd
from typing import List, Union
from utils.configs.parameters import gerar_caminho_database


def extrair_dados_database(nome_arquivo, camada):
    caminho_arquivo = gerar_caminho_database(nome_arquivo, camada)
    return pd.read_parquet(caminho_arquivo)


@st.cache_data
def carregar_dados():
    """Carrega os dados dos arquivos CSV."""
    d_periodo = extrair_dados_database("d_periodo.parquet", "gold")
    d_aluno = extrair_dados_database("d_aluno.parquet", "gold")
    d_disciplina = extrair_dados_database("d_disciplina.parquet", "gold")
    d_curso = extrair_dados_database("d_curso.parquet", "gold")
    d_situacao = extrair_dados_database("d_situacao.parquet", "gold")
    f_matricula_aluno = extrair_dados_database("f_situacao_metricula.parquet", "gold")
    f_situacao_periodo = extrair_dados_database("f_situacao_periodo.parquet", "gold")
    f_desempenho_academico = extrair_dados_database(
        "f_desempenho_academico.parquet", "gold"
    )
    periodo_atual = d_aluno.DS_PERIODO_INGRESSO_UFRJ.max()
    return (
        d_periodo,
        d_aluno,
        d_disciplina,
        d_curso,
        d_situacao,
        f_matricula_aluno,
        f_situacao_periodo,
        f_desempenho_academico,
        periodo_atual,
    )


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
