import streamlit as st
import os


# Definindo caminhos de imagem
logo_path = os.path.join("images", "horizontal_blue.png")
icon_image_path = os.path.join("images", "logo_small.png")

# Exibindo o logo
st.logo(image=logo_path, icon_image=icon_image_path)

# Definindo as páginas
home_page = st.Page(
    "home/home.py", title="Início", icon=":material/home:", default=True
)
alunos_page = st.Page(
    "alunos/home_aluno.py", title="Geral", icon=":material/dashboard:"
)
individual_aluno_page = st.Page(
    "alunos/individual_aluno.py", title="Individual", icon=":material/search:"
)
disciplinas_page = st.Page(
    "disciplinas/home_disciplina.py", title="Início", icon=":material/search:"
)

# Navegação
pages = {
    "Geral": [home_page],
    "Alunos": [alunos_page, individual_aluno_page],
    "Disciplinas": [disciplinas_page],
}

# Inicializando a navegação
navigation = st.navigation(pages)

# Executando a navegação
navigation.run()
