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


def obter_ultimo_cr(lista_cr):
    """
    Obtém o último valor de CR acumulado de uma lista de CRs.

    Args:
        lista_cra (list): Lista de CRs acumulados.

    Returns:
        float: O último CR acumulado da lista ou NaN se a lista estiver vazia.
    """
    if lista_cr:
        return lista_cr[-1]
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
        df_situacao_periodo.sort_values(["DS_MATRICULA_DRE", "DS_PERIODO"])
        .groupby("DS_MATRICULA_DRE")
        .agg({"VL_CR_PERIODO": list, "VL_CR_ACUMULADO": list})
        .rename(
            columns={
                "VL_CR_PERIODO": "lista_cr_periodo",
                "VL_CR_ACUMULADO": "lista_cr_acumulado",
            }
        )
        .reset_index()
    )

    teste = df_situacao_matricula.sort_values(
        by=["DS_MATRICULA_DRE", "VL_ANO", "VL_SEMESTRE"]
    )
    situacao_atual = teste.groupby("DS_MATRICULA_DRE").last().reset_index()
    situacao_atual = situacao_atual.drop(columns=["VL_ANO", "VL_SEMESTRE"])

    tabela = situacao_atual.merge(result, on="DS_MATRICULA_DRE", how="inner")

    tabela["CR_ACUMULADO_ATUAL"] = tabela["lista_cr_acumulado"].apply(obter_ultimo_cr)
    tabela["CR_ATUAL"] = tabela["lista_cr_periodo"].apply(obter_ultimo_cr)

    return tabela


def aplicar_filtros(
    df, text_search, cr_range, cra_range, situacao_selecionada, modalidade_selecionada
):
    """
    Aplica filtros ao DataFrame com base nos parâmetros fornecidos.

    Args:
        df (DataFrame): DataFrame original a ser filtrado.
        text_search (str): Texto de pesquisa para nome ou DRE.
        cr_range (tuple): Faixa de CR acumulado.
        situacao_selecionada (list): Lista de situações de matrícula selecionadas.
        modalidade_selecionada (list): Lista de modalidades de cota selecionadas.

    Returns:
        DataFrame: DataFrame filtrado de acordo com os parâmetros fornecidos.
    """
    # Filtragem por DRE ou Nome
    if text_search.isdigit():
        df = df[df["DS_MATRICULA_DRE"].astype(str).str.startswith(text_search)]
    elif text_search:
        df = df[df["DS_NOME_ALUNO"].str.contains(text_search, case=False, na=False)]

    # Filtragem por situação da matrícula
    if situacao_selecionada:
        df = df[df["DS_SITUACAO"].isin(situacao_selecionada)]

    # Filtragem por modalidade de cota
    if modalidade_selecionada:
        df = df[df["DS_MODALIDADE_COTA"].isin(modalidade_selecionada)]

    # Filtragem por intervalo de CR do periodo
    df = df[(df["CR_ATUAL"] >= cr_range[0]) & (df["CR_ATUAL"] <= cr_range[1])]

    # Filtragem por intervalo de CR acumulado
    df = df[
        (df["CR_ACUMULADO_ATUAL"] >= cra_range[0])
        & (df["CR_ACUMULADO_ATUAL"] <= cra_range[1])
    ]

    return df


def listagem_de_alunos(df_situacao_periodo, df_situacao_matricula, periodo_atual):
    """
    Exibe a listagem de alunos com opções de filtragem e pesquisa na interface Streamlit.

    Args:
        df_situacao_periodo (DataFrame): DataFrame contendo informações de CR por período.
        df_situacao_matricula (DataFrame): DataFrame contendo informações de situação de matrícula.
    """
    df = processar_dados_tabelas(df_situacao_periodo, df_situacao_matricula)

    # Criação de campos de pesquisa e filtragem
    with st.container():
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        with col1:
            text_search = st.text_input(
                "Pesquisar", placeholder="Digite o Nome ou DRE", key="dre_ou_nome"
            )
        with col2:
            lista_periodos = sorted(
                df_situacao_matricula["DS_PERIODO_INGRESSO_UFRJ"].unique()
            )
            ingresso_ufrj = st.select_slider(
                "Período de Ingresso na UFRJ",
                options=lista_periodos,
                value=(
                    lista_periodos[0],
                    lista_periodos[-1],
                ),  # Definir valor inicial como o primeiro e último período
                key="periodo_ingresso_ufrj",
            )
        with col3:
            lista_periodos = sorted(
                df_situacao_matricula["DS_PERIODO_INGRESSO_CURSO_ATUAL"].unique()
            )
            ingresso_curso = st.select_slider(
                "Período de Ingresso no Curso",
                options=lista_periodos,
                value=(
                    lista_periodos[0],
                    lista_periodos[-1],
                ),  # Definir valor inicial como o primeiro e último período
                key="periodo_ingresso_curso",
            )

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            situacoes_matricula = df["DS_SITUACAO"].unique()
            situacao_selecionada = st.multiselect(
                "Situação da Matrícula",
                situacoes_matricula,
                placeholder="Selecione as opções",
            )

        with col2:
            modalidades_cota = df["DS_MODALIDADE_COTA"].unique()
            modalidade_selecionada = st.multiselect(
                "Modalidade de Cota",
                modalidades_cota,
                placeholder="Selecione as opções",
            )

        with col3:
            cr_range = st.slider("CR Peíodo Atual", 0.0, 10.0, (0.0, 10.0), key="cr")

        with col4:
            cra_range = st.slider(
                "CR Acumulado Atual", 0.0, 10.0, (0.0, 10.0), key="cra"
            )

    # Aplicar os filtros ao DataFrame
    df_filtrado = aplicar_filtros(
        df,
        text_search,
        cr_range,
        cra_range,
        situacao_selecionada,
        modalidade_selecionada,
    )

    # Aplica filtro do período atual se não houver nenhum outro filtro
    if (
        not text_search
        and cra_range == (0.0, 10.0)
        and cr_range == (0.0, 10.0)
        and not situacao_selecionada
        and not modalidade_selecionada
    ):
        df_filtrado = df_filtrado[df_filtrado["DS_PERIODO"] == periodo_atual]

    # Cria um link a partir do DRE do aluno
    df_filtrado["DS_MATRICULA_DRE"] = df_filtrado["DS_MATRICULA_DRE"].apply(
        lambda dre: f"aluno_individual?dre={dre}"
    )
    # Exibição da tabela com os dados filtrados
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        selection_mode=["single-row"],
        column_order=(
            "DS_MATRICULA_DRE",
            "DS_NOME_ALUNO",
            "VL_IDADE_INGRESSO",
            "DS_CURSO_INGRESSO_UFRJ",
            "DS_MODALIDADE_COTA",
            "DS_SITUACAO",
            "lista_cr_periodo",
            "lista_cr_acumulado",
        ),
        column_config={
            "DS_NOME_ALUNO": "Nome Completo",
            "VL_IDADE_INGRESSO": "Idade de Ingresso",
            "DS_MATRICULA_DRE": st.column_config.LinkColumn(
                "Matrícula DRE",
                display_text="aluno_individual\\?dre=([^&\\s]*)",
            ),
            "DS_MODALIDADE_COTA": "Modalidade de Cota",
            "DS_SITUACAO": "Situação da Matrícula",
            "DS_CURSO_INGRESSO_UFRJ": "Curso de Ingresso",
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
dados = carregar_dados(
    datasets=[
        "d_aluno",
        "d_curso",
        "d_periodo",
        "d_situacao",
        "f_matricula_aluno",
        "f_situacao_periodo",
    ]
)
D_PERIODO = dados.get("d_periodo")
D_ALUNO = dados.get("d_aluno")
D_CURSO = dados.get("d_curso")
D_SITUACAO = dados.get("d_situacao")
F_MATRICULA_ALUNO = dados.get("f_matricula_aluno")
F_SITUACAO_PERIODO = dados.get("f_situacao_periodo")
PERIODO_ATUAL = dados.get("periodo_atual")

# Criar tabela Fato Matricula Aluno
dimensions = [D_PERIODO, D_ALUNO, D_CURSO, D_SITUACAO]
df_situacao_matricula = merge_dataframes(dimensions, F_MATRICULA_ALUNO)

# Criar tabela Fato Situação Período
dimensions_periodo = [D_ALUNO, D_PERIODO]
df_situacao_periodo = merge_dataframes(dimensions_periodo, F_SITUACAO_PERIODO)

# Criar tabela com a listagem de alunos
listagem_de_alunos(df_situacao_periodo, df_situacao_matricula, PERIODO_ATUAL)
