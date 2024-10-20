import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)


def criar_grafico_CR(
    df, coluna_valores, titulo="", y_min=-1, y_max=11, title_x="Período", title_y="CR"
):
    fig = go.Figure()

    # Adicionar a linha com os dados do CR
    fig.add_trace(
        go.Scatter(
            x=df["DS_PERIODO"],
            y=df[coluna_valores],
            mode="lines+markers",
            marker=dict(
                color=["red" if cr < 3 else "blue" for cr in df[coluna_valores]],
            ),
            name="CR",
        )
    )

    # Define os limites do eixo Y, se especificados
    fig.update_layout(
        title=titulo,
        xaxis_title=title_x,
        yaxis_title=title_y,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),  # Remove as margens
        yaxis=dict(range=[y_min, y_max]),
    )

    return st.plotly_chart(fig)


def grafico_de_crs(df):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histórico do CR Acumulado")
        criar_grafico_CR(df, "VL_CR_ACUMULADO", title_y="CRA")

    with col2:
        st.subheader("Histórico do CR do Período")
        criar_grafico_CR(df, "VL_CR_PERIODO")


def dados_gerais_aluno(df_aluno, periodo_atual):

    # Define o caminho atual e o caminho para a pasta de imagens
    CAMINHO_ATUAL = os.path.dirname(os.path.abspath(__file__))
    CAMINHO_IMG = os.path.abspath(os.path.join(CAMINHO_ATUAL, "../../images"))

    # Filtra o DataFrame para manter apenas o período atual (maior valor de DS_PERIODO)
    df_aluno = df_aluno[df_aluno["DS_PERIODO"] == df_aluno["DS_PERIODO"].max()]
    df_aluno = df_aluno.to_dict("records")[0]

    # Cria duas colunas: uma para a imagem do perfil e outra para os dados do aluno
    col1, col2 = st.columns([0.15, 0.85])

    with col1:
        # Define o caminho da imagem do perfil com base no sexo do aluno
        imagem = (
            f"{CAMINHO_IMG}/perfil_masculino_cat_3x4.png"
            if df_aluno["DS_SEXO"] == "Masculino"
            else f"{CAMINHO_IMG}/perfil_feminino_cat_3x4.jpg"
        )
        st.image(imagem)

    with col2:
        # Cria subcolunas para exibir os dados gerais do aluno
        subcol1, subcol2, subcol3, subcol4 = st.columns(4)

        # Dados que serão exibidos em cada subcoluna
        columns_data = [
            (
                subcol1,
                [
                    ("DRE", df_aluno["DS_MATRICULA_DRE"]),
                    ("Forma de Ingresso", df_aluno["DS_FORMA_INGRESSO"]),
                    ("Período de Ingresso UFRJ", df_aluno["DS_PERIODO_INGRESSO_UFRJ"]),
                ],
            ),
            (
                subcol2,
                [
                    ("Data de Nascimento", df_aluno["DT_NASCIMENTO"]),
                    ("Nota do Enem", df_aluno["VL_NOTA_ENEM"]),
                    (
                        "Período de Ingresso no Curso Atual",
                        df_aluno["DS_PERIODO_INGRESSO_CURSO_ATUAL"],
                    ),
                ],
            ),
            (
                subcol3,
                [
                    ("Sexo", df_aluno["DS_SEXO"]),
                    ("Modalidade de Cota", df_aluno["DS_MODALIDADE_COTA"]),
                    ("Logradouro", df_aluno["DS_LOGRADOURO"]),
                ],
            ),
            (
                subcol4,
                [
                    (
                        "Idade de Ingresso na UFRJ",
                        int(df_aluno["VL_IDADE_CURSO_ATUAL"]),
                    ),
                    ("Curso de Ingresso", df_aluno["DS_NOME_CURSO_INGRESSO"]),
                    ("Bairro", df_aluno["DS_BAIRRO"]),
                ],
            ),
        ]

    # Exibe os dados em cada subcoluna usando text_input (desabilitado para exibição apenas)
    for subcol, fields in columns_data:
        for label, value in fields:
            subcol.text_input(label, value, disabled=True)


def tabela_aprovacao_disciplina(dados_aluno, desemenho_disciplinas):
    # Converte a coluna para numérico, substituindo valores não convertíveis por NaN
    desemenho_disciplinas["VL_GRAU_DISCIPLINA"] = pd.to_numeric(
        desemenho_disciplinas["VL_GRAU_DISCIPLINA"], errors="coerce"
    )

    # Filtra apenas os valores numéricos
    df_desempenho = desemenho_disciplinas[
        desemenho_disciplinas["VL_GRAU_DISCIPLINA"].notnull()
    ]

    # Agrupa e calcula a média
    df_disciplina_agrupado = (
        df_desempenho[
            [
                "DS_PERIODO",
                "CD_DISCIPLINA",
                "DS_NOME_DISCIPLINA",
                "VL_GRAU_DISCIPLINA",
            ]
        ]
        .groupby(["DS_PERIODO", "CD_DISCIPLINA", "DS_NOME_DISCIPLINA"])[
            "VL_GRAU_DISCIPLINA"
        ]
        .mean()
        .round(1)
        .reset_index(name="VL_GRAU_DISCIPLINA_MEDIA")
    )

    dados_aluno = dados_aluno[
        [
            "DS_PERIODO",
            "CD_DISCIPLINA",
            "DS_NOME_DISCIPLINA",
            "VL_GRAU_DISCIPLINA",
            "DS_SITUACAO",
            "DS_SITUACAO_DETALHADA",
        ]
    ]
    dados_aluno = dados_aluno.set_index(
        ["DS_PERIODO", "CD_DISCIPLINA", "DS_NOME_DISCIPLINA"]
    )
    df_disciplina_agrupado = df_disciplina_agrupado.set_index(
        ["DS_PERIODO", "CD_DISCIPLINA", "DS_NOME_DISCIPLINA"]
    )

    dados_aluno = dados_aluno.join(
        df_disciplina_agrupado,
        how="left",
    ).reset_index()

    df_reprovacaoes = (
        dados_aluno[dados_aluno["DS_SITUACAO_DETALHADA"] != "Aprovado"]
        .sort_values("DS_PERIODO")
        .reset_index(drop=True)
    )
    df_aprovacaoes = (
        dados_aluno[
            (dados_aluno["DS_SITUACAO_DETALHADA"] == "Aprovado")
            & (dados_aluno["VL_GRAU_DISCIPLINA"] != "T")
        ]
        .sort_values("DS_PERIODO")
        .reset_index(drop=True)
    )
    df_transferencias = dados_aluno[dados_aluno["VL_GRAU_DISCIPLINA"] == "T"]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Disciplinas")
        tab1, tab2, tab3, tab4 = st.tabs(
            ["✅ Aprovações", "❌ Reprovações", "⬇️ Transferências", "📚 Detalhes"]
        )
        with tab1:
            # st.subheader("Aprovações")
            st.dataframe(
                df_aprovacaoes,
                use_container_width=True,
                column_order=(
                    "DS_PERIODO",
                    "CD_DISCIPLINA",
                    "DS_NOME_DISCIPLINA",
                    "VL_GRAU_DISCIPLINA",
                    "VL_GRAU_DISCIPLINA_MEDIA",
                ),
                column_config={
                    "DS_PERIODO": "Período",
                    "CD_DISCIPLINA": "Código",
                    "DS_NOME_DISCIPLINA": "Disciplina",
                    "VL_GRAU_DISCIPLINA": "Nota Final",
                    "VL_GRAU_DISCIPLINA_MEDIA": "Média da Turma",
                },
                hide_index=True,
            )

        with tab2:
            # st.subheader("Reprovações")
            st.dataframe(
                df_reprovacaoes,
                use_container_width=True,
                column_order=(
                    "DS_PERIODO",
                    "CD_DISCIPLINA",
                    "DS_NOME_DISCIPLINA",
                    "VL_GRAU_DISCIPLINA",
                    "DS_SITUACAO_DETALHADA",
                    "VL_GRAU_DISCIPLINA_MEDIA",
                ),
                column_config={
                    "DS_PERIODO": "Período",
                    "CD_DISCIPLINA": "Código",
                    "DS_NOME_DISCIPLINA": "Disciplina",
                    "VL_GRAU_DISCIPLINA": "Nota Final",
                    "DS_SITUACAO_DETALHADA": "Situação Final",
                    "VL_GRAU_DISCIPLINA_MEDIA": "Média da Turma",
                },
                hide_index=True,
            )
        with tab3:
            st.dataframe(
                df_transferencias,
                use_container_width=True,
                column_order=(
                    "DS_PERIODO",
                    "CD_DISCIPLINA",
                    "DS_NOME_DISCIPLINA",
                    "VL_GRAU_DISCIPLINA",
                ),
                column_config={
                    "DS_PERIODO": "Período",
                    "CD_DISCIPLINA": "Código",
                    "DS_NOME_DISCIPLINA": "Disciplina",
                    "VL_GRAU_DISCIPLINA": "Nota Final",
                },
                hide_index=True,
            )

        with tab4:
            reprovacao_agg = (
                df_reprovacaoes.groupby(
                    ["CD_DISCIPLINA", "DS_NOME_DISCIPLINA", "DS_SITUACAO"]
                )
                .size()
                .reset_index(name="QUANTIDADE")
                .sort_values("QUANTIDADE", ascending=False)
            )
            st.dataframe(
                reprovacao_agg,
                use_container_width=True,
                column_config={
                    "CD_DISCIPLINA": "Código",
                    "DS_NOME_DISCIPLINA": "Disciplina",
                    "DS_SITUACAO": "Situação",
                    "QUANTIDADE": "Total de Reprovação",
                },
                hide_index=True,
            )


def cabecalho_e_metricas(df_aluno, df_periodo_aluno, periodo_atual):
    # Seleciona apenas as colunas necessárias e ordena os períodos
    df_periodo_aluno = df_periodo_aluno[
        ["DS_PERIODO", "VL_CR_ACUMULADO", "VL_CR_PERIODO"]
    ]
    df_periodo_aluno = df_periodo_aluno.sort_values("DS_PERIODO", ascending=False)

    # Filtra o DataFrame para manter apenas o período atual (maior valor de DS_PERIODO)
    df_aluno = df_aluno[df_aluno["DS_PERIODO"] == df_aluno["DS_PERIODO"].max()]

    df_aluno = df_aluno.to_dict("records")[0]

    # Verifica se existem pelo menos dois períodos para calcular a variação
    if len(df_periodo_aluno) > 1:
        # Seleciona o último e o penúltimo período para calcular a variação
        df_ultimo_periodo = df_periodo_aluno.iloc[0]
        df_penultimo_periodo = df_periodo_aluno.iloc[1]

        # Calcula a variação do CRA e do CR do período
        cra_variacao = (
            df_ultimo_periodo["VL_CR_ACUMULADO"]
            - df_penultimo_periodo["VL_CR_ACUMULADO"]
        )
        cr_variacao = (
            df_ultimo_periodo["VL_CR_PERIODO"] - df_penultimo_periodo["VL_CR_PERIODO"]
        )
    else:
        # Se houver apenas um período, não há variação
        df_ultimo_periodo = df_periodo_aluno.iloc[0]
        cra_variacao = None
        cr_variacao = None

    # Exibe as informações do aluno e as métricas calculadas
    st.header(df_aluno["NM_ALUNO"], divider="rainbow")

    col1, col2, col3, col4 = st.columns([0.58, 0.14, 0.14, 0.14])
    col1.metric("Situação da Matrícula", df_aluno["DS_SITUACAO_DETALHADA"])
    col2.metric(
        "CR Acumulado",
        df_ultimo_periodo["VL_CR_ACUMULADO"],
        f"{cra_variacao:.2f}" if cra_variacao is not None else "-",
    )
    col3.metric(
        "CR do Período",
        df_ultimo_periodo["VL_CR_PERIODO"],
        f"{cr_variacao:.2f}" if cr_variacao is not None else "-",
    )
    col4.metric(
        "Quant. Períodos Integralizados", df_aluno["VL_PERIODOS_INTEGRALIZADOS"]
    )  # Atualize conforme necessário
    st.markdown("\n")


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
        df = df[df["NM_ALUNO"].str.contains(text_search, case=False, na=False)]

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
            "NM_ALUNO",
            "VL_IDADE_INGRESSO",
            "DS_CURSO_INGRESSO_UFRJ",
            "DS_MODALIDADE_COTA",
            "DS_SITUACAO",
            "lista_cr_periodo",
            "lista_cr_acumulado",
        ),
        column_config={
            "NM_ALUNO": "Nome Completo",
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


def gerar_perfil_aluno(
    dre,
    df_situacao_matricula,
    df_situacao_periodo,
    df_desempenho_academico,
    periodo_atual,
):
    # Filtrando dataframes para o Aluno especifico
    df_situacao_matricula_filtrado = df_situacao_matricula[
        df_situacao_matricula["DS_MATRICULA_DRE"] == dre
    ]
    df_situacao_periodo_filtrado = df_situacao_periodo[
        df_situacao_periodo["DS_MATRICULA_DRE"] == dre
    ]
    df_desempenho_academico_filtrado = df_desempenho_academico[
        df_desempenho_academico["DS_MATRICULA_DRE"] == dre
    ]

    with st.container():
        cabecalho_e_metricas(
            df_situacao_matricula_filtrado,
            df_situacao_periodo_filtrado,
            periodo_atual,
        )

    with st.container():
        dados_gerais_aluno(df_situacao_matricula_filtrado, periodo_atual)

    with st.container():
        with st.expander("Períodos Trancados"):
            # Filtrar os períodos trancados
            periodos_trancados = sorted(
                df_situacao_matricula_filtrado[
                    df_situacao_matricula_filtrado["DS_SITUACAO"] == "Trancada"
                ]["DS_PERIODO"].values
            )

            # Verificar se há períodos trancados
            if len(periodos_trancados) > 0:
                # Exibir cada período trancado
                for periodo in periodos_trancados:
                    st.write(f"- {periodo}")
            else:
                st.write("Não há períodos trancados.")
        st.divider()

    with st.container():
        grafico_de_crs(df_situacao_periodo_filtrado)
        st.divider()

    with st.container():
        tabela_aprovacao_disciplina(
            df_desempenho_academico_filtrado, df_desempenho_academico
        )


def main():
    # Carregamento dos dados
    dados = carregar_dados(
        datasets=[
            "d_aluno",
            "d_curso",
            "d_periodo",
            "d_disciplina",
            "d_situacao",
            "f_matricula_aluno",
            "f_situacao_periodo",
            "f_desempenho_academico",
        ]
    )

    # Criar tabela Fato Matricula Aluno
    df_situacao_matricula = merge_dataframes(
        [
            dados.get("d_periodo"),
            dados.get("d_aluno"),
            dados.get("d_curso"),
            dados.get("d_situacao"),
        ],
        dados.get("f_matricula_aluno"),
    )

    # Criar tabela Fato Desempenho Academico
    df_desempenho_academico = merge_dataframes(
        [
            dados.get("d_periodo"),
            dados.get("d_aluno"),
            dados.get("d_situacao"),
            dados.get("d_disciplina"),
        ],
        dados.get("f_desempenho_academico"),
    )

    # Criar tabela Fato Situação Período
    df_situacao_periodo = merge_dataframes(
        [dados.get("d_aluno"), dados.get("d_periodo")], dados.get("f_situacao_periodo")
    )

    # Verifica DRE nos parâmetros da URL
    dre = st.query_params.get("dre")

    if dre:
        # Gera o perfil do alunos com seus dados pessoais
        gerar_perfil_aluno(
            dre,
            df_situacao_matricula,
            df_situacao_periodo,
            df_desempenho_academico,
            dados.get("periodo_atual"),
        )
    else:
        st.header("Alunos")
        # Criar tabela com a listagem de alunos
        listagem_de_alunos(
            df_situacao_periodo, df_situacao_matricula, dados.get("periodo_atual")
        )


main()
