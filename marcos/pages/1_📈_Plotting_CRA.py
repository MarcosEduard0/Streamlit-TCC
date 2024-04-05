import streamlit as st
import pandas as pd
import numpy as np
import time

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


def main():
    st.title("Dashboard de Alunos")

    with st.container():
        st.write("---")
        st.subheader("Análise de CRA")

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
            "Anos",
            max_value=int(max(anos)),
            min_value=int(min(anos)),
            value=(int(min(anos)), int(max(anos))),
        )

        cond = (media_cra["ano"].between(*anos)) & (
            media_cra["semestre"].isin(semestres_select)
        )
        df = media_cra[cond]

        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        last_rows = df.iloc[:1, 2:4]  # Primeira linha do DataFrame
        chart = st.line_chart(last_rows, x="periodo", y="Média CRA")
        total_linhas = len(df)

        for i in range(1, total_linhas + 1):
            new_rows = pd.concat([last_rows.iloc[:1, :], df.iloc[:i, 2:4]], axis=0)
            status_text.text("%i%% Complete" % int(i / total_linhas * 100))
            chart.add_rows(new_rows)
            progress_bar.progress(int(i / total_linhas * 100))
            last_rows = new_rows
            time.sleep(0.05)

        progress_bar.empty()
        st.button("Rodar Novamente")

    with st.container():
        st.write("---")

        st.subheader("Quantidade de Evasão")


if __name__ == "__main__":
    main()
