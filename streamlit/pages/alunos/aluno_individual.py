import streamlit as st

from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)


(
    D_PERIODO,
    D_ALUNO,
    D_DISCIPLINA,
    D_CURSO,
    F_MATRICULA_ALUNO,
    F_SITUACAO_PERIODO,
    PERIODO_ATUAL,
) = carregar_dados()

# Configuração da página Streamlit

dre = st.query_params.get("dre")
if dre:
    aluno = D_ALUNO[D_ALUNO["matricula_dre"] == int(dre)]
    st.header(aluno["nome_completo"].values[0], divider="rainbow")
    st.write(aluno)

    aluno = aluno.to_dict("records")[0]

    col1, col2 = st.columns([0.15, 0.85])

    with col1:
        st.image(
            "images/retrato_feminino.png",
            width=180,
        )
        st.write(aluno["nome_completo"])
    with col2:
        subcol1, subcol2, subcol3, subcol4 = st.columns(4)
        with subcol1:
            st.text_input("DRE", aluno["matricula_dre"], disabled=True)

        with subcol2:
            st.text_input("Sexo", aluno["sexo"], disabled=True)
            st.text_input("Forma de Ingresso", aluno["forma_ingresso"], disabled=True)

        with subcol3:
            st.text_input("Data de Nascimento", aluno["data_nascimento"], disabled=True)

else:
    text_search = st.text_input("Pesquisar", placeholder="Digite o Nome ou DRE")
