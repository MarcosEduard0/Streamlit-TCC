import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)


def criar_grafico_CR(df, coluna_valores, titulo=""):
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

    fig.update_layout(
        title=titulo,
        xaxis_title="Período",
        yaxis_title="CR",
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),  # Remove as margens
    )

    return fig


def grafico_de_crs(df):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Histórico do CR Acumulado")
        fig_acumulado = criar_grafico_CR(df, "VL_CR_ACUMULADO")
        st.plotly_chart(fig_acumulado)

    with col2:
        st.subheader("Histórico do CR do Período")
        fig_periodo = criar_grafico_CR(df, "VL_CR_PERIODO")
        st.plotly_chart(fig_periodo)


def dados_gerais_aluno(df_aluno):
    df_aluno = df_aluno.to_dict("records")[0]

    st.header(df_aluno["DS_NOME_ALUNO"], divider="rainbow")

    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.image("images/retrato_feminino.png")

    with col2:
        subcol1, subcol2, subcol3, subcol4 = st.columns(4)
        subcol1.text_input("DRE", df_aluno["DS_MATRICULA_DRE"], disabled=True)
        subcol1.text_input(
            "Forma de Ingresso", df_aluno["DS_FORMA_INGRESSO"], disabled=True
        )
        subcol1.text_input(
            "Período de Ingresso UFRJ",
            df_aluno["DS_PERIODO_INGRESSO_UFRJ"],
            disabled=True,
        )

        subcol2.text_input("Sexo", df_aluno["DS_SEXO"], disabled=True)
        subcol2.text_input(
            "Modalidade de Cota", df_aluno["DS_MODALIDADE_COTA"], disabled=True
        )
        subcol2.text_input(
            "Situação da Matrícula", df_aluno["DS_SITUACAO_DETALHADA"], disabled=True
        )

        subcol3.text_input(
            "Data de Nascimento", df_aluno["DT_NASCIMENTO"], disabled=True
        )
        subcol3.text_input("Nota do Enem", df_aluno["VL_NOTA_ENEM"], disabled=True)

        subcol4.text_input(
            "Idade de Ingresso na UFRJ",
            int(df_aluno["VL_IDADE_CURSO_ATUAL"]),
            disabled=True,
        )
        subcol4.text_input(
            "Curso de Ingresso", df_aluno["DS_NOME_CURSO_INGRESSO"], disabled=True
        )


# Carregamento dos dados
(
    D_PERIODO,
    D_ALUNO,
    D_DISCIPLINA,
    D_CURSO,
    D_SITUACAO,
    F_MATRICULA_ALUNO,
    F_SITUACAO_PERIODO,
    F_DESEMPENHO_ACADEMICO,
    PERIODO_ATUAL,
) = carregar_dados()

# Criar tabela Fato Matricula Aluno
df_situacao_matricula = merge_dataframes(
    [D_PERIODO, D_ALUNO, D_CURSO, D_SITUACAO], F_MATRICULA_ALUNO
)

# Criar tabela Fato Situação Período
df_situacao_periodo = merge_dataframes([D_ALUNO, D_PERIODO], F_SITUACAO_PERIODO)

# Verifica DRE nos parâmetros da URL
dre = st.query_params.get("dre")
if dre:
    with st.sidebar:
        st.write("oi")
    df_situacao_matricula = df_situacao_matricula[
        df_situacao_matricula["DS_MATRICULA_DRE"] == dre
    ]
    df_situacao_periodo = df_situacao_periodo[
        df_situacao_periodo["DS_MATRICULA_DRE"] == dre
    ]

    dados_gerais_aluno(df_situacao_matricula)

    st.write("---")
    grafico_de_crs(df_situacao_periodo)
else:
    st.text_input("Pesquisar", placeholder="Digite o Nome ou DRE")
