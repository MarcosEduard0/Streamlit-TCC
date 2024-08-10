import pandas as pd
import streamlit as st
import pandas as pd
from typing import List, Union


@st.cache_data
def carregar_dados():
    """Carrega os dados dos arquivos CSV."""
    data_path = "../database/gold/"
    d_periodo = pd.read_csv(data_path + "d_periodo.csv")
    d_aluno = pd.read_csv(data_path + "d_aluno.csv")
    d_disciplina = pd.read_csv(data_path + "d_disciplina.csv")
    d_curso = pd.read_csv(data_path + "d_curso.csv")
    f_matricula_aluno = pd.read_csv(data_path + "f_situacao_metricula.csv")
    f_situacao_periodo = pd.read_csv(data_path + "f_situacao_periodo.csv")
    periodo_atual = d_aluno.periodo_ingresso_ufrj.max()
    return (
        d_periodo,
        d_aluno,
        d_disciplina,
        d_curso,
        f_matricula_aluno,
        f_situacao_periodo,
        periodo_atual,
    )


def merge_dataframes(
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
