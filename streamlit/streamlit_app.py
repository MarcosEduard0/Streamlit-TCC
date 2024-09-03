import streamlit as st
import os

st.set_page_config(layout="wide")

CAMINHO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# Caminho para o diretório que você quer listar (neste caso, a raiz do seu projeto)
caminho = "/mount/src/streamlit-tcc/"

# Listar os arquivos e diretórios dentro do caminho
try:
    arquivos_e_diretorios = os.listdir(caminho)
    st.write("Conteúdo do diretório:")
    for item in arquivos_e_diretorios:
        st.write(item)
except FileNotFoundError as e:
    st.write(f"Erro: {e}")


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
