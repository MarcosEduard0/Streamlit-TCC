import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)


def criar_grafico_CR(df, coluna_valores, titulo="", y_min=-1, y_max=11):
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
        xaxis_title="Período",
        yaxis_title="CR",
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),  # Remove as margens
        yaxis=dict(range=[y_min, y_max]),
    )

    return st.plotly_chart(fig)


def grafico_de_crs(df):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histórico do CR Acumulado")
        criar_grafico_CR(df, "VL_CR_ACUMULADO")

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
        how="inner",
    ).reset_index()

    df_reprovacaoes = (
        dados_aluno[dados_aluno["DS_SITUACAO_DETALHADA"] != "Aprovado"]
        .sort_values("DS_PERIODO")
        .reset_index(drop=True)
    )
    df_aprovacaoes = (
        dados_aluno[dados_aluno["DS_SITUACAO_DETALHADA"] == "Aprovado"]
        .sort_values("DS_PERIODO")
        .reset_index(drop=True)
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Disciplinas")
        tab1, tab2, tab3 = st.tabs(["✅ Aprovações", "❌ Reprovações", "📛 Detalhes"])
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
    st.header(df_aluno["DS_NOME_ALUNO"], divider="rainbow")

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
        # with st.sidebar:
        #     st.write("oi")
        df_situacao_matricula_filtrado = df_situacao_matricula[
            df_situacao_matricula["DS_MATRICULA_DRE"] == dre
        ]
        df_situacao_periodo_filtrado = df_situacao_periodo[
            df_situacao_periodo["DS_MATRICULA_DRE"] == dre
        ]
        df_desempenho_academico_filtrado = df_desempenho_academico[
            df_desempenho_academico["DS_MATRICULA_DRE"] == dre
        ]

        cabecalho_e_metricas(
            df_situacao_matricula_filtrado,
            df_situacao_periodo_filtrado,
            dados.get("periodo_atual"),
        )

        dados_gerais_aluno(df_situacao_matricula_filtrado, dados.get("periodo_atual"))
        st.divider()

        grafico_de_crs(df_situacao_periodo_filtrado)
        st.divider()

        tabela_aprovacao_disciplina(
            df_desempenho_academico_filtrado, df_desempenho_academico
        )
    else:
        st.text_input("Pesquisar", placeholder="Digite o Nome ou DRE")


main()
