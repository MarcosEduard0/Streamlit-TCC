import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Desenvolvimento TCC")


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
st.title("Dashboard de Alunos")

with st.container():
    st.write("---")
    st.subheader("Analise de CRA")

    fato_periodo = F_DESEMPENHO_ACADEMICO.merge(
        D_PERIODO, on=["sk_d_periodo"], how="inner"
    )
    media_cra = (
        fato_periodo.groupby(["ano", "semestre", "periodo"])["cr_acumulado"]
        .mean()
        .reset_index(name="Média CRA")
    )

    semestres = media_cra["semestre"].unique().tolist()
    semestres_select = st.sidebar.multiselect(
        "Semestres", semestres, default=semestres[1:3]
    )

    anos = media_cra["ano"].unique().tolist()
    anos = st.sidebar.slider(
        "Anos", max_value=max(anos), min_value=min(anos), value=(min(anos), max(anos))
    )

    cond = (media_cra["ano"].between(*anos)) & (
        media_cra["semestre"].isin(semestres_select)
    )
    df = media_cra[cond]

    st.line_chart(df, x="periodo", y="Média CRA")

    fato_periodo_aluno = pd.merge(fato_periodo, D_ALUNO, on="sk_d_aluno", how="inner")

    st.subheader("Quantidade de Evação")


with st.container():
    st.write("---")
