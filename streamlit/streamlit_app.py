import streamlit as st

st.set_page_config(layout="wide")

# Exibindo o logo
st.logo(image="images/logo_horizontal.png", icon_image="images/logo_ic.png")

# Definindo as páginas
home = st.Page(
    "pages/home/home.py", title="Início", icon=":material/home:", default=True
)
aluno_home = st.Page(
    "pages/alunos/aluno_home.py", title="Geral", icon=":material/dashboard:"
)
aluno_individual_page = st.Page(
    "pages/alunos/aluno_individual.py", title="Individual", icon=":material/search:"
)
disciplinas_page = st.Page(
    "pages/disciplinas/home_disciplina.py", title="Início", icon=":material/search:"
)

individual_disciplina_page = st.Page(
    "pages/disciplinas/individual_disciplina.py",
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
    "Geral": [home],
    "Alunos": [aluno_home, aluno_individual_page],
    "Disciplinas": [disciplinas_page, individual_disciplina_page],
    "Base de Dados": [base_dados],
}

# Inicializando a navegação
navigation = st.navigation(pages)

# Executando a navegação
navigation.run()
