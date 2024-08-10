import streamlit as st
import numpy as np

from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)

# -----------------------------------------------------------
# Script de Criação da Interface Streamlit para página inicial de Alunos
# Autor:
# Data de Criação:
# Descrição: Este script cria uma interface Streamlit para exibir e filtrar
# dados dos alunos, incluindo opções de pesquisa por nome ou matrícula,
# seleção por situação de matrícula, modalidade de cota e intervalo de CR acumulado.
# -----------------------------------------------------------


def obter_ultimo_cra(lista_cra):
    """
    Obtém o último valor de CR acumulado de uma lista de CRs.

    Args:
        lista_cra (list): Lista de CRs acumulados.

    Returns:
        float: O último CR acumulado da lista ou NaN se a lista estiver vazia.
    """
    if lista_cra:
        return lista_cra[-1]
    else:
        return np.nan


def processar_dados_tabelas(df_situacao_periodo, df_situacao_matricula):
    """
    Processa e combina os dados das tabelas de situação de período e matrícula.

    Args:
        df_situacao_periodo (DataFrame): DataFrame contendo informações de CR por período.
        df_situacao_matricula (DataFrame): DataFrame contendo informações de situação de matrícula.

    Returns:
        DataFrame: DataFrame combinado com CR acumulado atual e listas de CRs por período e acumulado.
    """
    result = (
        df_situacao_periodo.sort_values(["matricula_dre", "periodo"])
        .groupby("matricula_dre")
        .agg({"cr_periodo": list, "cr_acumulado": list})
        .rename(
            columns={
                "cr_periodo": "lista_cr_periodo",
                "cr_acumulado": "lista_cr_acumulado",
            }
        )
        .reset_index()
    )

    teste = df_situacao_matricula.sort_values(by=["matricula_dre", "ano", "semestre"])
    situacao_atual = teste.groupby("matricula_dre").last().reset_index()
    situacao_atual = situacao_atual.drop(columns=["ano", "semestre"])

    tabela = situacao_atual.merge(result, on="matricula_dre", how="inner")

    tabela["cr_acumulado"] = tabela["lista_cr_acumulado"].apply(obter_ultimo_cra)

    return tabela


def listagem_de_alunos(df_situacao_periodo, df_situacao_matricula):
    """
    Exibe a listagem de alunos com opções de filtragem e pesquisa na interface Streamlit.

    Args:
        df_situacao_periodo (DataFrame): DataFrame contendo informações de CR por período.
        df_situacao_matricula (DataFrame): DataFrame contendo informações de situação de matrícula.
    """
    df = processar_dados_tabelas(df_situacao_periodo, df_situacao_matricula)

    # Criação de campos de pesquisa e filtragem
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            text_search = st.text_input("Pesquisar", placeholder="Digite o Nome ou DRE")
        with col2:
            situacoes_matricula = df["situacao_matricula_simplificada"].unique()
            option = st.multiselect(
                "Situação da Matrícula",
                situacoes_matricula,
                placeholder="Selecione as opções",
            )

    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            cr_range = st.slider("CR Acumulado Atual", 0.0, 10.0, (0.0, 10.0))

        with col2:
            conta = df["modalidade_cota"].unique()
            option = st.multiselect(
                "Modalidade de Cota",
                conta,
                placeholder="Selecione as opções",
            )

    # Filtragem dos dados com base nos inputs do usuário
    if text_search.isdigit():
        df_search = df[df["matricula_dre"].astype(str).str.startswith(text_search)]
    elif text_search:
        df_search = df[
            df["nome_completo"].str.contains(text_search, case=False, na=False)
        ]
    else:
        df_search = df  # Exibe o dataframe completo se não houver pesquisa de texto

    # Filtra pelo intervalo de CR acumulado
    df_search = df_search[
        (df_search["cr_acumulado"] >= cr_range[0])
        & (df_search["cr_acumulado"] <= cr_range[1])
    ]

    # Aplica filtro do período atual se não houver nenhum outro filtro
    if text_search == "" and cr_range == (0.0, 10.0):
        df_search = df_search[df_search["periodo"] == PERIODO_ATUAL]

    df_search["matricula_dre"] = df_search["matricula_dre"].apply(
        lambda dre: f"aluno_individual?dre={dre}"
    )

    # Exibição da tabela com os dados filtrados
    st.dataframe(
        df_search,
        use_container_width=True,
        selection_mode=["single-row"],
        column_order=(
            "matricula_dre",
            "nome_completo",
            "idade",
            "curso_ingresso_ufrj",
            "situacao_matricula_simplificada",
            "lista_cr_periodo",
            "lista_cr_acumulado",
        ),
        column_config={
            "nome_completo": "Nome Completo",
            "idade": "Idade de Ingresso",
            "matricula_dre": st.column_config.LinkColumn(
                "Matrícula DRE",
                display_text="aluno_individual\\?dre=([^&\\s]*)",
            ),
            # "matricula_dre": st.column_config.NumberColumn(
            #     "DRE",
            #     help="Matrícula do Aluno",
            #     format="%d",
            # ),
            "situacao_matricula_simplificada": "Situação da Matrícula",
            "curso_ingresso_ufrj": "Curso de Ingresso",
            "lista_cr_acumulado": st.column_config.AreaChartColumn(
                "CR Acumulado", y_min=0, y_max=10
            ),
            "lista_cr_periodo": st.column_config.AreaChartColumn(
                "CR por Período", y_min=0, y_max=10
            ),
        },
        hide_index=True,
    )


st.markdown("# Alunos")

# Carregamento dos dados
(
    D_PERIODO,
    D_ALUNO,
    D_DISCIPLINA,
    D_CURSO,
    F_MATRICULA_ALUNO,
    F_SITUACAO_PERIODO,
    PERIODO_ATUAL,
) = carregar_dados()

# Criar tabela Fato Matricula Aluno
dimensions = [D_PERIODO, D_ALUNO, D_CURSO]
fact = F_MATRICULA_ALUNO
keys = ["sk_d_periodo", "sk_d_aluno", "sk_d_curso"]
df_situacao_matricula = merge_dataframes(dimensions, fact, keys)

# Criar tabela Fato Situação Período
dimensions_periodo = [D_ALUNO, D_PERIODO]
fact_periodo = F_SITUACAO_PERIODO
keys_periodo = ["sk_d_aluno", "sk_d_periodo"]
df_situacao_periodo = merge_dataframes(dimensions_periodo, fact_periodo, keys_periodo)

# Criar tabela com a listagem de alunos
listagem_de_alunos(df_situacao_periodo, df_situacao_matricula)
