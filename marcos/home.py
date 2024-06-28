import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="COAA - UFRJ",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Trabalho desenvolvido para o trabalho de conclusão de curso!",
    },
)


@st.cache_data
def carregar_dados():
    """Carrega os dados dos arquivos CSV."""
    d_periodo = pd.read_csv("data/refined/d_periodo.csv")
    d_aluno = pd.read_csv("data/refined/d_aluno.csv")
    d_disciplina = pd.read_csv("data/refined/d_disciplina.csv")
    f_matricula_aluno = pd.read_csv("data/refined/f_situacao_metricula.csv")
    f_situacao_periodo = pd.read_csv("data/refined/f_situacao_periodo.csv")
    periodo_atual = d_aluno.periodo_ingresso_ufrj.max()
    return (
        d_periodo,
        d_aluno,
        d_disciplina,
        f_matricula_aluno,
        f_situacao_periodo,
        periodo_atual,
    )


def grafico_situacao_matricula_periodo(dataframe):
    data = dataframe[dataframe["situacao_matricula"] != "Ativa"]
    data = (
        data.groupby(["situacao_matricula", "periodo"])
        .size()
        .reset_index(name="quantidade")
    )

    data.sort_values("periodo", inplace=True)

    fig = px.bar(
        data,
        x="periodo",
        y="quantidade",
        color="situacao_matricula",
        labels={
            "quantidade": "Quantidade",
            "periodo": "Período",
            "situacao_matricula": "Situação da Matrícula",
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
        dataframe.groupby(["periodo"])["cr_acumulado"].mean().reset_index(name="media")
    )
    data["media"] = data["media"].round(2)
    data.sort_values("periodo", inplace=True)

    fig = px.line(
        data,
        x="periodo",
        y="media",
        labels={"media": "Média CRA", "periodo": "Período"},
        markers=True,
    )

    st.plotly_chart(fig)


def grafico_situacao_matricula_periodo_ingresso(dataframe):
    data = (
        dataframe.groupby(["situacao_matricula", "periodo_ingresso_ufrj"])
        .size()
        .reset_index(name="quantidade")
    )

    data.sort_values("periodo_ingresso_ufrj", inplace=True)

    # Calcula o total de cada período de ingresso
    total_por_periodo = (
        data.groupby("periodo_ingresso_ufrj")["quantidade"]
        .sum()
        .reset_index(name="total")
    )

    # Junta os totais ao dataframe original
    data = data.merge(total_por_periodo, on="periodo_ingresso_ufrj")

    fig = px.bar(
        data,
        x="periodo_ingresso_ufrj",
        y="quantidade",
        color="situacao_matricula",
        labels={
            "quantidade": "Quantidade",
            "periodo_ingresso_ufrj": "Período de Ingresso na UFRJ",
            "situacao_matricula": "Situação da Matrícula",
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


def metricas_atuais(df, periodo_atual):
    """Exibe as métricas atuais dos alunos."""
    df = df[df["periodo"] == periodo_atual]

    df_situacao = (
        df.groupby(["situacao_matricula"]).size().reset_index(name="quantidade")
    )
    df_genero = df.groupby(["sexo"]).size().reset_index(name="quantidade")

    quant_homens = df_genero[df_genero["sexo"] == "Masculino"]["quantidade"].values[0]
    quant_mulheres = df_genero[df_genero["sexo"] == "Feminino"]["quantidade"].values[0]
    quant_ativa = df_situacao[df_situacao["situacao_matricula"] == "Ativa"][
        "quantidade"
    ].values[0]
    quant_trancado = df_situacao[df_situacao["situacao_matricula"] == "Trancada"][
        "quantidade"
    ].values[0]

    col1, col2 = st.columns(2)
    col1.metric("Ativa", quant_ativa)
    col2.metric("Trancado", quant_trancado)
    # col3.metric("Mulheres", quant_mulheres)
    # col4.metric("Homens", quant_homens)


def main():
    (
        D_PERIODO,
        D_ALUNO,
        D_DISCIPLINA,
        F_MATRICULA_ALUNO,
        F_SITUACAO_PERIODO,
        PERIODO_ATUAL,
    ) = carregar_dados()

    st.header("Sistema de Análises Acadêmica")
    st.subheader(f"Perído Atual: {PERIODO_ATUAL}")
    st.markdown(f"Esta página tem como objetivo analisar dados gerais do curso.")

    # Combina os dataframes
    df_situacao_matricula = pd.merge(
        F_MATRICULA_ALUNO, D_PERIODO, on="sk_d_periodo", how="inner"
    )
    df_situacao_matricula = pd.merge(
        df_situacao_matricula, D_ALUNO, on="sk_d_aluno", how="inner"
    )

    df_situacao_periodo = pd.merge(
        F_SITUACAO_PERIODO, D_PERIODO, on="sk_d_periodo", how="inner"
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


if __name__ == "__main__":
    main()
