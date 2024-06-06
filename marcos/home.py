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


D_PERIODO = pd.read_csv("data/refined/d_periodo.csv")
D_ALUNO = pd.read_csv("data/refined/d_aluno.csv")
D_DISCIPLINA = pd.read_csv("data/refined/d_disciplina.csv")
F_DESEMPENHO_ACADEMICO = pd.read_csv("data/refined/f_desempenho_academico.csv")
F_MATRICULA_ALUNO = carregar_dados_matricula()


def metricas(df):
    # quant_homens = df[df["sexo"] == "M"]['quantidade']
    df_grouped = df.groupby("sexo")["quantidade"].sum().reset_index()
    quant_homens = df_grouped[df_grouped["sexo"] == "M"]["quantidade"]
    quant_mulheres = df_grouped[df_grouped["sexo"] == "F"]["quantidade"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mulheres", quant_mulheres, "-20")
    col2.metric("Homens", quant_homens, "56")
    col3.metric("Abandono", "20%", "-4%")
    col4.metric("Trancamento", "10%", "6%")


def main():
    st.write("## Hello Word! Análise Gerais 👋")
    st.markdown(
        """
        Esta página tem como objetivo analisar dados gerais do curso.
    """
    )

    # Combina os dataframes
    df = pd.merge(F_MATRICULA_ALUNO, D_PERIODO, on="sk_d_periodo", how="inner")
    df = pd.merge(df, D_ALUNO, on="sk_d_aluno", how="inner")

    df_filtered = (
        df.groupby(["periodo", "situacao_matricula", "ano", "semestre", "sexo"])
        .size()
        .reset_index(name="quantidade")
    )

    # Filtros
    situacao_matricula_options = st.sidebar.multiselect(
        "Escolha o tipo de situação da matrícula",
        df_filtered["situacao_matricula"].unique().tolist(),
        ["Ativa"],
    )

    if not situacao_matricula_options:
        st.error("Por favor, selecione uma situação.")
    else:
        semestres = sorted(df_filtered["semestre"].unique().tolist())
        semestres_select = st.sidebar.multiselect(
            "Semestres", semestres, default=[1, 2]
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

        # Primeiro container
        with st.container():
            metricas(df_filtered)

        # Segundo container
        with st.container():
            st.write("---")
            st.subheader("Análise de Matrícula")
            df_grouped = (
                df_filtered.groupby(["periodo", "semestre"])["quantidade"]
                .sum()
                .reset_index()
            )
            st.line_chart(df_grouped, x="periodo", y="quantidade")


if __name__ == "__main__":
    main()
