import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError

st.set_page_config(page_title="DataFrame Demo", page_icon="📊")

st.markdown("# Aluno Específico")
st.sidebar.header("DataFrame Demo")
st.write("""Analisando um único aluno""")


@st.cache_data
def get_data():
    try:
        D_PERIODO = pd.read_csv("data/refined/d_periodo.csv")
        D_ALUNO = pd.read_csv("data/refined/d_aluno.csv")
        D_CURSO = pd.read_csv("data/refined/d_curso.csv")
        D_DISCIPLINA = pd.read_csv("data/refined/d_disciplina.csv")
        F_DESEMPENHO_ACADEMICO = pd.read_csv("data/refined/f_desempenho_academico.csv")

        df = pd.merge(
            F_DESEMPENHO_ACADEMICO, D_PERIODO, on="sk_d_periodo", how="inner"
        ).drop("sk_d_periodo", axis=1)
        df = pd.merge(df, D_ALUNO, on="sk_d_aluno", how="inner").drop(
            "sk_d_aluno", axis=1
        )
        df = pd.merge(df, D_DISCIPLINA, on="sk_d_disciplina", how="inner").drop(
            "sk_d_disciplina", axis=1
        )
        df = pd.merge(df, D_CURSO, on="sk_d_curso", how="inner").drop(
            "sk_d_curso", axis=1
        )

        return df, D_ALUNO
    except URLError as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None, None


# Carregar dados
df, D_ALUNO = get_data()

# Verificar se os dados foram carregados corretamente
if df is not None and D_ALUNO is not None:
    lista_dre = D_ALUNO["matricula_dre"].tolist()

    if not lista_dre:
        st.error("Nenhum DRE encontrado.")
    else:
        # Adicionar uma seleção de DRE
        selected_dre = st.selectbox("Selecione o DRE do aluno", lista_dre)

        # Filtrar o DataFrame para o DRE selecionado
        aluno_df_historico = df[df["matricula_dre"] == selected_dre]
        aluno_df = D_ALUNO[D_ALUNO["matricula_dre"] == selected_dre]

        # Mostrar dados do aluno
        st.write(f"Dados do aluno: {aluno_df['nome_completo'].values[0]}")
        st.write(f"Periodo de Ingresso: {aluno_df['nome_completo'].values[0]}")
        st.dataframe(aluno_df_historico)

        # # Criar e mostrar gráfico com Altair
        # chart = (
        #     alt.Chart(aluno_df_historico)
        #     .mark_bar()
        #     .encode(x="nome_disciplina", y="grau_disciplina", color="periodo")
        #     .properties(width=600, height=400)
        # )

        # Criar e mostrar gráfico com Altair
        aluno_df_historico["periodo_disciplina"] = (
            aluno_df_historico["periodo"]
            + " - "
            + aluno_df_historico["nome_disciplina"]
        )

        chart = (
            alt.Chart(aluno_df_historico)
            .mark_bar()
            .encode(
                x=alt.X(
                    "periodo_disciplina:N",
                    sort=alt.EncodingSortField(field="periodo"),
                    title="Período - Disciplina",
                ),
                y=alt.Y("grau_disciplina:Q", title="Nota Obtida"),
                color="periodo:N",
                tooltip=["nome_disciplina", "periodo", "grau_disciplina"],
            )
            .properties(width=800, height=400, title="Desempenho Acadêmico do Aluno")
        )

        st.altair_chart(chart)
else:
    st.error("Falha ao carregar os dados.")
