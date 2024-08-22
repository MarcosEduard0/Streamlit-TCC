import os
import sys
import papermill as pm
from colorama import Fore, Style, init

# Inicializa o colorama
init()

# Constantes para os caminhos dos notebooks
NOTEBOOK_BRONZE = "../ETL/bronze/landing_bronze.ipynb"
NOTEBOOK_SILVER = "../ETL/silver/bronze_silver.ipynb"
NOTEBOOKS_DIMENSOES = [
    "../ETL/gold/dimensoes/d_aluno.ipynb",
    "../ETL/gold/dimensoes/d_curso.ipynb",
    "../ETL/gold/dimensoes/d_disciplina.ipynb",
    "../ETL/gold/dimensoes/d_situacao.ipynb",
    "../ETL/gold/dimensoes/d_periodo.ipynb",
]
NOTEBOOKS_FATOS = [
    "../ETL/gold/fatos/f_desempenho_academico.ipynb",
    "../ETL/gold/fatos/f_situacao_matricula.ipynb",
    "../ETL/gold/fatos/f_situacao_periodo.ipynb",
]


# Função para executar um notebook Jupyter
def executar_notebook(notebook_path, output_path=None):
    print(
        f"{Fore.LIGHTBLACK_EX}  |- Notebook a ser executado: {notebook_path}{Style.RESET_ALL}"
    )
    notebook_output_path = output_path or notebook_path.replace(
        ".ipynb", "_executed.ipynb"
    )
    try:
        pm.execute_notebook(notebook_path, notebook_output_path)
        os.remove(notebook_output_path)
        print(f"{Fore.GREEN}  |- Concluído!{Style.RESET_ALL}")
    except pm.PapermillExecutionError as e:
        print(
            f"{Fore.RED}\nErro ao executar {notebook_path}\nVerifique o notebook de saída em: {notebook_output_path}\n{str(e)}{Style.RESET_ALL}"
        )
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}\nErro inesperado: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


# Função para executar uma lista de notebooks
def executar_lista_notebooks(notebooks):
    for notebook in notebooks:
        executar_notebook(os.path.abspath(notebook))


# Função principal para executar o pipeline
def executar_pipeline():
    print(f"{Fore.LIGHTCYAN_EX}|- Iniciando Pipeline de ETL...\n{Style.RESET_ALL}")

    # Etapa 1: Landing -> Bronze
    print(f"{Fore.YELLOW}|- ETAPA 1: Landing -> Bronze{Style.RESET_ALL}")
    executar_notebook(os.path.abspath(NOTEBOOK_BRONZE))
    print(f"{Fore.YELLOW}|- ETAPA 1: Finalizada com sucesso!\n{Style.RESET_ALL}")

    # Etapa 2: Bronze -> Silver
    print(f"{Fore.YELLOW}|- ETAPA 2: Bronze -> Silver{Style.RESET_ALL}")
    executar_notebook(os.path.abspath(NOTEBOOK_SILVER))
    print(f"{Fore.YELLOW}|- ETAPA 2: Finalizada com sucesso!\n{Style.RESET_ALL}")

    # Etapa 3: Silver -> Gold
    print(f"{Fore.YELLOW}|- ETAPA 3: Silver -> Gold{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  |- DIMENSÕES:{Style.RESET_ALL}")
    executar_lista_notebooks(NOTEBOOKS_DIMENSOES)

    print(f"\n{Fore.YELLOW}  |- FATOS:{Style.RESET_ALL}")
    executar_lista_notebooks(NOTEBOOKS_FATOS)

    print(f"{Fore.YELLOW}|- ETAPA 3: Finalizada com sucesso!\n{Style.RESET_ALL}")
    print(f"{Fore.LIGHTCYAN_EX}Pipeline de ETL concluído com sucesso!{Style.RESET_ALL}")


# Execução do pipeline
if __name__ == "__main__":
    executar_pipeline()
