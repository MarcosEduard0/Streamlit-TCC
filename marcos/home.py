import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="COAA - UFRJ",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        # "Get Help": "https://github.com/MarcosEduard0",
        # "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "Trabalho desenvolvido para o trabalho de conclusão de curso!",
    },
)


@st.cache_data
def carregamento_tabelas():
    D_ALUNO = pd.read_csv("data/d_aluno.csv")
    D_CURSO = pd.read_csv("data/d_curso.csv")
    D_DISCIPLINA = pd.read_csv("data/d_disciplina.csv")
    D_PERIODO = pd.read_csv("data/d_periodo.csv")
    F_DESEMPENHO_ACADEMICO = pd.read_csv("data/f_desempenho_academico.csv")

    D_PERIODO["periodo"] = (
        D_PERIODO["ano"].astype(str) + "/" + D_PERIODO["semestre"].astype(str)
    )

    return D_ALUNO, D_CURSO, D_DISCIPLINA, D_PERIODO, F_DESEMPENHO_ACADEMICO


D_ALUNO, D_CURSO, D_DISCIPLINA, D_PERIODO, F_DESEMPENHO_ACADEMICO = (
    carregamento_tabelas()
)

st.write("## Hello Word! Analise Gerais 👋")

# st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Esta página tem como objetivo analisar dados gerais do curso.
"""
)


with st.container():
    st.write("---")
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    st.bar_chart(chart_data)
