import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Alunos", page_icon="🧑‍🎓")

st.markdown("# Alunos")


# st.sidebar.header("Alunos")
@st.cache_data
def carregar_dados():
    """Carrega os dados dos arquivos CSV."""
    d_periodo = pd.read_csv("data/refined/d_periodo.csv")
    d_aluno = pd.read_csv("data/refined/d_aluno.csv")
    d_disciplina = pd.read_csv("data/refined/d_disciplina.csv")
    d_curso = pd.read_csv("data/refined/d_curso.csv")
    f_matricula_aluno = pd.read_csv("data/refined/f_situacao_metricula.csv")
    f_situacao_periodo = pd.read_csv("data/refined/f_situacao_periodo.csv")
    periodo_atual = d_aluno.periodo_ingresso_ufrj.max()
    return (
        d_periodo,
        d_aluno,
        d_disciplina,
        d_curso,
        f_matricula_aluno,
        f_situacao_periodo,
        periodo_atual,
    )


def main():
    (
        D_PERIODO,
        D_ALUNO,
        D_DISCIPLINA,
        D_CURSO,
        F_MATRICULA_ALUNO,
        F_SITUACAO_PERIODO,
        PERIODO_ATUAL,
    ) = carregar_dados()

    df = pd.DataFrame(
        {
            "name": ["Roadmap", "Extras", "Issues"],
            "url": [
                "https://roadmap.streamlit.app",
                "https://extras.streamlit.app",
                "https://issues.streamlit.app",
            ],
            "stars": [random.randint(0, 1000) for _ in range(3)],
            "views_history": [
                [random.randint(0, 5000) for _ in range(30)] for _ in range(3)
            ],
        }
    )

    # Combina os dataframes
    df_situacao_matricula = pd.merge(
        D_PERIODO, F_MATRICULA_ALUNO, on="sk_d_periodo", how="inner"
    )
    df_situacao_matricula = pd.merge(
        D_ALUNO, df_situacao_matricula, on="sk_d_aluno", how="inner"
    )
    df_situacao_matricula = pd.merge(
        df_situacao_matricula, D_CURSO, on="sk_d_curso", how="inner"
    )
    df_situacao_matricula.drop(
        ["sk_d_periodo", "sk_d_aluno", "sk_d_curso"], inplace=True, axis=1
    )

    st.dataframe(
        df,
        column_config={
            "name": "App name",
            "stars": st.column_config.NumberColumn(
                "Github Stars",
                help="Number of stars on GitHub",
                format="%d ⭐",
            ),
            "url": st.column_config.LinkColumn("App URL"),
            "views_history": st.column_config.LineChartColumn(
                "Views (past 30 days)", y_min=0, y_max=5000
            ),
        },
        hide_index=True,
    )

    teste = df_situacao_matricula.sort_values(by=["matricula_dre", "ano", "semestre"])
    situacao_atual = teste.groupby("matricula_dre").last().reset_index()
    situacao_atual = situacao_atual.drop(columns=["ano", "semestre"])

    st.dataframe(
        situacao_atual,
        use_container_width=True,
        column_order=(
            "matricula_dre",
            "nome_completo",
            "curso_ingresso_ufrj",
            "situacao_matricula",
        ),
        column_config={
            "nome_completo": "Nome Completo",
            "matricula_dre": st.column_config.NumberColumn(
                "DRE",
                help="Matrícula do Aluno",
                format="%d",
            ),
            "situacao_matricula": "Situação da Matrícula",
            "curso_ingresso_ufrj": "Curso de Ingresso",
            "views_history": st.column_config.LineChartColumn(
                "Views (past 30 days)", y_min=0, y_max=5000
            ),
        },
        hide_index=True,
    )


if __name__ == "__main__":
    main()
