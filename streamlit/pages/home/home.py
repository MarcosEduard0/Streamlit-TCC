import streamlit as st
import pandas as pd
import plotly.express as px

from utils.auxiliary_functions.all_auxiliary_functions import carregar_dados

# st.set_page_config(
#     page_title="COAA - UFRJ",
#     page_icon="🏠",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         "About": "Trabalho desenvolvido para o trabalho de conclusão de curso!",
#     },
# )


def grafico_situacao_matricula_periodo(dataframe):
    data = dataframe[dataframe["DS_SITUACAO"] != "Ativa"]
    data = (
        data.groupby(["DS_SITUACAO", "DS_PERIODO"])
        .size()
        .reset_index(name="quantidade")
    )

    data.sort_values("DS_PERIODO", inplace=True)

    fig = px.bar(
        data,
        x="DS_PERIODO",
        y="quantidade",
        color="DS_SITUACAO",
        labels={
            "quantidade": "Quantidade",
            "DS_PERIODO": "Período",
            "DS_SITUACAO": "Situação da Matrícula",
        },
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(title="Situação da Matrícula", traceorder="normal"),
        barmode="stack",
    )
    st.plotly_chart(fig)


def grafico_media_cra_periodo(dataframe):

    data = (
        dataframe.groupby(["DS_PERIODO"])["VL_CR_ACUMULADO"]
        .mean()
        .reset_index(name="media")
    )
    data["media"] = data["media"].round(2)
    data.sort_values("DS_PERIODO", inplace=True)

    fig = px.line(
        data,
        x="DS_PERIODO",
        y="media",
        labels={"media": "Média CRA", "DS_PERIODO": "Período"},
        markers=True,
    )

    st.plotly_chart(fig)


def grafico_situacao_matricula_periodo_ingresso(dataframe):
    data = (
        dataframe.groupby(["DS_SITUACAO", "DS_PERIODO_INGRESSO_UFRJ"])
        .size()
        .reset_index(name="quantidade")
    )

    data.sort_values("DS_PERIODO_INGRESSO_UFRJ", inplace=True)

    # Calcula o total de cada período de ingresso
    total_por_periodo = (
        data.groupby("DS_PERIODO_INGRESSO_UFRJ")["quantidade"]
        .sum()
        .reset_index(name="total")
    )

    # Junta os totais ao dataframe original
    data = data.merge(total_por_periodo, on="DS_PERIODO_INGRESSO_UFRJ")

    fig = px.bar(
        data,
        x="DS_PERIODO_INGRESSO_UFRJ",
        y="quantidade",
        color="DS_SITUACAO",
        labels={
            "quantidade": "Quantidade",
            "DS_PERIODO_INGRESSO_UFRJ": "Período de Ingresso na UFRJ",
            "DS_SITUACAO": "Situação da Matrícula",
        },
    )

    # Customiza o hovertemplate para incluir o total
    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "Período: %{x}",
                "Quantidade: %{y}",
                "Total no Período: %{customdata[0]}",
            ]
        ),
        customdata=data[["total"]].values,
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(title="Situação da Matrícula", traceorder="normal"),
        barmode="stack",
    )

    st.plotly_chart(fig)


def periodos_anteriores(periodo_atual, num_semestres):
    ano, semestre = periodo_atual.split("/")
    ano = int(ano)
    semestre = int(semestre)

    total_semestres = (ano * 2 + semestre) - num_semestres

    ano_anterior = total_semestres // 2
    semestre_anterior = total_semestres % 2

    if semestre_anterior == 0:
        semestre_anterior = 2
        ano_anterior -= 1

    return f"{ano_anterior}/{semestre_anterior}"


def metricas_atuais(df, periodo_atual):
    """Exibe as métricas atuais dos alunos."""
    df_atual = df[df["DS_PERIODO"] == periodo_atual]

    # Obter período anterior
    periodo_anterior = periodos_anteriores(periodo_atual, 1)
    df_anterior = df[df["DS_PERIODO"] == periodo_anterior]

    df_situacao = (
        df_atual.groupby(["DS_SITUACAO"]).size().reset_index(name="quantidade")
    )
    # df_genero = df_atual.groupby(["DS_SEXO"]).size().reset_index(name="quantidade")

    media_enem_atual = round(df_atual["VL_NOTA_ENEM"].mean(), 2)
    media_enem_anterior = round(df_anterior["VL_NOTA_ENEM"].mean(), 2)

    # Calcular a variação percentual
    if media_enem_anterior != 0:
        variacao_enem = round(
            ((media_enem_atual - media_enem_anterior) / media_enem_anterior) * 100, 2
        )
    else:
        variacao_enem = 0

    quant_ativa = df_situacao[df_situacao["DS_SITUACAO"] == "Ativa"][
        "quantidade"
    ].values[0]
    quant_trancado = df_situacao[df_situacao["DS_SITUACAO"] == "Trancada"][
        "quantidade"
    ].values[0]
    media_idade_atual = int(df_atual["VL_IDADE_CURSO_ATUAL"].mean())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ativos", quant_ativa)
    col2.metric("Trancados", quant_trancado)
    col3.metric("Média Idade", media_idade_atual)
    col4.metric("Média Enem", media_enem_atual, f"{variacao_enem}%")


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

st.header("Sistema de Análises Acadêmica")
st.subheader(f"Perído Atual: {PERIODO_ATUAL}")
st.markdown(f"Situação Atual dos alunos.")

# Combina os dataframes
df_situacao_matricula = pd.merge(
    F_MATRICULA_ALUNO, D_PERIODO, on="SK_D_PERIODO", how="left"
)
df_situacao_matricula = pd.merge(
    df_situacao_matricula, D_ALUNO, on="SK_D_ALUNO", how="left"
)

df_situacao_matricula = pd.merge(
    df_situacao_matricula, D_SITUACAO, on="SK_D_SITUACAO", how="left"
)

# Fato Periodo
df_situacao_periodo = pd.merge(
    F_SITUACAO_PERIODO, D_PERIODO, on="SK_D_PERIODO", how="left"
)

with st.container():
    metricas_atuais(df_situacao_matricula, PERIODO_ATUAL)
    st.write("---")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Total de Alunos por Situação")
        grafico_situacao_matricula_periodo(df_situacao_matricula)

    with col2:
        st.subheader("Média CRA por Perído")
        grafico_media_cra_periodo(df_situacao_periodo)

# Segundo container
with st.container():
    st.subheader("Análise de Matrícula Periodo de Ingresso")
    grafico_situacao_matricula_periodo_ingresso(df_situacao_matricula)
