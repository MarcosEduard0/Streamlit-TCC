import pandas as pd
from utils.configs.parameters import gerar_caminho_database


def extrair_dados_database(nome_arquivo, camada):
    caminho_arquivo = gerar_caminho_database(nome_arquivo, camada)
    extensao = nome_arquivo.split(".")[-1]

    if extensao == "parquet":
        return pd.read_parquet(caminho_arquivo)
    elif extensao in ["xlsx", "xls"]:
        return pd.read_excel(caminho_arquivo)
    else:
        raise ValueError(f"Formato de arquivo não suportado: {extensao.upper()}")


def carregar_dados_database(dataframe, nome_arquivo, camada, formato: str = "parquet"):
    formato = formato.lower()
    nome_arquivo = f"{nome_arquivo}.{formato}"
    caminho_arquivo = gerar_caminho_database(nome_arquivo, camada)

    try:
        if formato == "parquet":
            dataframe.to_parquet(caminho_arquivo, index=False)
        elif formato == "csv":
            dataframe.to_csv(caminho_arquivo, index=False)
        else:
            raise ValueError(f"Formato não suportado: {formato}")

        print(f"Arquivo {nome_arquivo}.{formato} salvo com sucesso na camada {camada}.")

    except Exception as e:
        raise ValueError(f"Falha ao salvar arquivo na camada {camada}: {e}")
