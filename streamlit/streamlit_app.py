import streamlit as st
import os

st.set_page_config(
    page_title="COAA - UFRJ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "Trabalho desenvolvido para o trabalho de conclusão de curso!",
    },
)

CAMINHO_ATUAL = os.path.dirname(os.path.abspath(__file__))
# Exibindo o logo
st.logo(
    image=f"{CAMINHO_ATUAL}/images/horizontal_blue.png",
    icon_image=f"{CAMINHO_ATUAL}/images/icon_blue.png",
)


# Definindo as páginas
home = st.Page(
    "pages/home/home.py", title="Início", icon=":material/home:", default=True
)
aluno_home = st.Page(
    "pages/alunos/aluno_home.py", title="Geral", icon=":material/home:"
)
aluno_individual_page = st.Page(
    "pages/alunos/aluno_individual.py", title="Individual", icon=":material/search:"
)
disciplinas_page = st.Page(
    "pages/disciplinas/disciplina_home.py", title="Geral", icon=":material/dashboard:"
)

individual_disciplina_page = st.Page(
    "pages/disciplinas/disciplina_individual.py",
    title="Individual",
    icon=":material/search:",
)

base_dados = st.Page(
    "pages/base/base_dados.py",
    title="Base de Dados",
    icon=":material/search:",
)

# Navegação
pages = {
    # "Geral": [home],
    "Alunos": [aluno_home, aluno_individual_page],
    "Disciplinas": [disciplinas_page, individual_disciplina_page],
    "Base de Dados": [base_dados],
}

# Inicializando a navegação
navigation = st.navigation(pages)

# Executando a navegação
navigation.run()
