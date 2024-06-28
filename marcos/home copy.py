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


# @st.cache_data
# def carregar_dados():
D_PERIODO = pd.read_csv("data/refined/d_periodo.csv")
D_ALUNO = pd.read_csv("data/refined/d_aluno.csv")
D_DISCIPLINA = pd.read_csv("data/refined/d_disciplina.csv")
F_MATRICULA_ALUNO = pd.read_csv("data/refined/f_situacao_metricula.csv")


def metricas_atuais(df):
    df_genero = df.groupby("sexo")["quantidade"].sum().reset_index()
    df_situacao = df.groupby("situacao_matricula")["quantidade"].sum().reset_index()

    quant_homens = df_genero[df_genero["sexo"] == "M"]["quantidade"]
    quant_mulheres = df_genero[df_genero["sexo"] == "F"]["quantidade"]
    quant_cancelado = df_situacao[df_situacao["situacao_matricula"] == "Cancelada"][
        "quantidade"
    ]
    quant_trancado = df_situacao[df_situacao["situacao_matricula"] == "Trancada"][
        "quantidade"
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mulheres", quant_mulheres)
    col2.metric("Homens", quant_homens)
    col3.metric("Evasão", quant_cancelado)
    col4.metric("Trancamento", quant_trancado)


def main():
    st.header("Sitema de Análises Acadêmica")
    st.markdown(
        """
        Esta página tem como objetivo analisar dados gerais do curso.
    """
    )
    st.sidebar.header("Filtros")
    # Combina os dataframes
    df = pd.merge(F_MATRICULA_ALUNO, D_PERIODO, on="sk_d_periodo", how="inner")
    df = pd.merge(df, D_ALUNO, on="sk_d_aluno", how="inner")

    # df_filtered = (
    #     df.groupby(["periodo", "situacao_matricula", "ano", "semestre", "sexo"])
    #     .size()
    #     .reset_index(name="quantidade")
    # )
    # # Filtros
    # situacao_matricula_options = st.sidebar.multiselect(
    #     "Escolha o tipo de situação da matrícula",
    #     df_filtered["situacao_matricula"].unique().tolist(),
    #     ["Ativa"],
    # )

    # if not situacao_matricula_options:
    #     st.error("Por favor, selecione uma situação.")

    # else:
    # semestres = sorted(df_filtered["semestre"].unique().tolist())
    # semestres_select = st.sidebar.multiselect(
    #     "Semestres", semestres, default=[1, 2]
    # )

    # anos = df_filtered["ano"].unique().tolist()
    # anos = st.sidebar.slider(
    #     "Anos",
    #     max_value=max(anos),
    #     min_value=min(anos),
    #     value=(min(anos), max(anos)),
    # )

    # cond_container1 = (
    #     (df_filtered["ano"].between(*anos))
    #     & (df_filtered["semestre"].isin(semestres_select))
    #     & (df_filtered["situacao_matricula"].isin(situacao_matricula_options))
    # )

    # cond_container2 = (
    #     (df_filtered["ano"].between(*anos))
    #     & (df_filtered["semestre"].isin(semestres_select))
    #     & (df_filtered["situacao_matricula"].isin(situacao_matricula_options))
    # )

    # df_metricas = df_filtered[cond_container1]
    # df_cr_periodo = df_filtered[cond_container2]

    tab1, tab2 = st.tabs(["Período Atual", "Período Total"])
    with st.container():
        # st.header("A cat")
        metricas_atuais(df)
        st.write("---")
    col1, col2 = st.columns(2)

    # Segundo container
    with col1:
        # st.header("A cat")
        st.subheader("Análise de Matrícula")
        data = (
            df.groupby(["situacao_matricula", "periodo"])
            .size()
            .reset_index(name="quantidade")
        )

        data.sort_values("periodo", inplace=True)
        fig = px.bar(
            data,
            x="periodo",
            y="quantidade",
            color="situacao_matricula",
            # title="Análise de Matrícula",
            labels={"quantidade": "Quantidade", "periodo": "Período"},
        )
        # Desativando a interatividade da legenda
        fig.update_layout(
            showlegend=True,
            legend=dict(title="Situação da Matrícula", traceorder="normal"),
            barmode="stack",
        )

        st.plotly_chart(fig)

    with col2:
        # st.header("A cat")
        st.subheader("Análise da Média do CRA")
        # data = np.random.randn(10, 1)
        # st.line_chart(data)
        test = px.data.stocks()
        fig = px.line(test, x="date", y="GOOG")
        st.plotly_chart(fig)

    # Segundo container
    with st.container():
        st.subheader("Análise de Matrícula Periodo de Ingresso")
        data = (
            df.groupby(["situacao_matricula", "periodo_ingresso_ufrj"])
            .size()
            .reset_index(name="quantidade")
        )

        data.sort_values("periodo_ingresso_ufrj", inplace=True)
        fig = px.bar(
            data,
            x="periodo_ingresso_ufrj",
            y="quantidade",
            color="situacao_matricula",
            # title="Análise de Matrícula",
            labels={
                "quantidade": "Quantidade",
                "periodo_ingresso_ufrj": "Período de Ingresso UFRJ",
            },
        )
        # Desativando a interatividade da legenda
        fig.update_layout(
            showlegend=True,
            legend=dict(title="Situação da Matrícula", traceorder="normal"),
            barmode="stack",
        )

        st.plotly_chart(fig)


if __name__ == "__main__":
    main()
