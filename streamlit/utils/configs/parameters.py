import os

# Diretório do arquivo atual
CAMINHO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# Caminho completo para o acesso ao database
CAMINHO_DATABASE = os.path.abspath(os.path.join(CAMINHO_ATUAL, "../../../database"))


def gerar_caminho_database(nome_arquivo: str, camada: str) -> str:
    return f"{CAMINHO_DATABASE}/{camada}/{nome_arquivo}"
