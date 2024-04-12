import streamlit as st
import pandas as pd

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
def carregar_dados_matricula():
    return pd.read_csv("data/refined/f_matricula_aluno.csv")


def metricas():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mulheres", "279", "-20")
    col2.metric("Homens", "1704", "56")
    col3.metric("Abandono", "20%", "-4%")
    col4.metric("Trancamento", "10%", "6%")


def main():
    st.write("## Hello Word! Análise Gerais 👋")
    st.markdown(
        """
        Esta página tem como objetivo analisar dados gerais do curso.
    """
    )

    with st.container():
        metricas()

    with st.container():
        st.write("---")
        st.subheader("Analise de Matricula")

        # Carregando os dados apenas quando necessário
        F_MATRICULA_ALUNO = carregar_dados_matricula()

        df_filtered = (
            F_MATRICULA_ALUNO.groupby(
                ["periodo", "situacao_matricula", "ano", "semestre"]
            )
            .size()
            .reset_index(name="quantidade")
        )

        situacao_matricula_options = st.sidebar.multiselect(
            "Escolha o tipo de situação da matrícula",
            df_filtered["situacao_matricula"].unique().tolist(),
            ["Ativa"],
        )

        semestres = sorted(df_filtered["semestre"].unique().tolist())
        semestres_select = st.sidebar.multiselect(
            "Semestres", semestres, default=semestres[1:3]
        )

        anos = df_filtered["ano"].unique().tolist()
        anos = st.sidebar.slider(
            "Anos",
            max_value=max(anos),
            min_value=min(anos),
            value=(min(anos), max(anos)),
        )

        cond = (
            (df_filtered["ano"].between(*anos))
            & (df_filtered["semestre"].isin(semestres_select))
            & (df_filtered["situacao_matricula"].isin(situacao_matricula_options))
        )
        df_filtered = df_filtered[cond]

        st.bar_chart(df_filtered, x="periodo", y="quantidade")


if __name__ == "__main__":
    main()
