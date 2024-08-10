import streamlit as st
import os


# Definindo caminhos de imagem
logo_path = os.path.join("images", "ovo.png")
icon_image_path = os.path.join("images", "logo_small.png")

st.set_page_config(layout="wide")

# Exibindo o logo
st.logo(image=logo_path, icon_image=icon_image_path)

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

# Navegação
pages = {
    "Geral": [home],
    "Alunos": [aluno_home, aluno_individual_page],
    "Disciplinas": [disciplinas_page, individual_disciplina_page],
}

# Inicializando a navegação
navigation = st.navigation(pages)

# Executando a navegação
navigation.run()
