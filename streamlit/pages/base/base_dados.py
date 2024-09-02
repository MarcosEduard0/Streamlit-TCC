import streamlit as st
import pandas as pd
import os
from utils.configs.parameters import gerar_caminho_database
import subprocess as sub
import time


# Função para salvar o arquivo carregado
def save_uploaded_file(uploaded_file, path):
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Arquivo salvo com sucesso!")
    return path


# Função para carregar e mostrar a barra de progresso
def load_data(uploaded_file):
    dataframe = pd.read_excel(uploaded_file)
    st.write(dataframe)


st.title("Carregar Base de Dados")

arquivo = gerar_caminho_database("arquivo_anonimizado_v2.xlsx", "landing")
# Verifica se já existe uma base carregada
if os.path.exists(arquivo):
    st.warning(" AVISO: Já existe uma base de dados carregada. ", icon="⚠️")
    # st.markdown(" 👋")

# Se não há base carregada, permite ao usuário carregar uma nova base
uploaded_file = st.file_uploader("Escolha um arquivo para carregar na base")

if uploaded_file is not None:
    # Salvar o arquivo carregado
    caminho_arquivo = save_uploaded_file(uploaded_file, arquivo)

    # Carregar os dados para exibição
    load_data(caminho_arquivo)

    # Executar o pipeline ETL
    if st.button("Enviar"):
        progress_file = "progress.txt"  # Arquivo para monitorar o progresso
        with st.spinner("Executando Pipeline ETL..."):
            process = sub.Popen(
                ["python", "../ETL/etl_run.py"],
                stdout=sub.PIPE,
                stderr=sub.PIPE,
                text=True,
            )
            progress_bar = st.progress(0)

            while process.poll() is None:
                # Ler a porcentagem de progresso do arquivo
                if os.path.exists(progress_file):
                    with open(progress_file, "r") as f:
                        progress_percentage = float(f.read().strip())
                        progress_bar.progress(int(progress_percentage))
                time.sleep(1)  # Espera 1 segundo antes de verificar novamente

            stdout, stderr = process.communicate()
            if process.returncode == 0:
                st.success("Pipeline ETL executado com sucesso!")
            else:
                st.error(f"Erro ao executar o pipeline ETL: {stderr}")

            # Remover arquivo de progresso
            if os.path.exists(progress_file):
                os.remove(progress_file)
