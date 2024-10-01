import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)

# Função de ordenação de períodos
def ordenar_periodos(periodos):
    periodos_ordenados = sorted(periodos, key=lambda x: (int(x.split("/")[0]), int(x.split("/")[1])))
    return periodos_ordenados

def main():
    # Carregar dados
    dados = carregar_dados(
        datasets=[
            "d_curso",
            "d_periodo",
            "d_disciplina",
            "d_situacao",
            "f_desempenho_academico",
        ]
    )
    
    # Criar tabela Fato Desempenho Academico
    df_desempenho_academico = merge_dataframes(
        [
            dados.get("d_periodo"),
            dados.get("d_situacao"),
            dados.get("d_disciplina"),
        ],
        dados.get("f_desempenho_academico")
    )

    # Obter lista de disciplinas únicas para a barra de pesquisa
    disciplinas_unicas = df_desempenho_academico["DS_NOME_DISCIPLINA"].unique().tolist()
    disciplinas_unicas.sort()  # Ordenar alfabeticamente

    # Definir a disciplina padrão
    disciplina_padrao = "Banco de Dados I"

    # Barra de pesquisa com selectbox para selecionar a disciplina
    disciplina_selecionada = st.selectbox(
        "Pesquisar Disciplina",
        options=disciplinas_unicas,
        index=disciplinas_unicas.index(disciplina_padrao) if disciplina_padrao in disciplinas_unicas else 0
    )

    # Verifica se uma disciplina foi selecionada
    if disciplina_selecionada:
        
        # Filtrar dados pela disciplina selecionada
        df_filtrado_disciplina = df_desempenho_academico[
            df_desempenho_academico["DS_NOME_DISCIPLINA"] == disciplina_selecionada
        ]

        # Filtrar períodos que não terminam com "/0"
        periodos_filtrados = [periodo for periodo in df_filtrado_disciplina["DS_PERIODO"].unique() if not periodo.endswith("/0")]

        # Ordenar os períodos de forma cronológica
        periodos_ordenados = ordenar_periodos(periodos_filtrados)

        # Seletor de intervalo de períodos
        periodo_inicio, periodo_fim = st.select_slider(
            "Selecione o intervalo de períodos",
            options=periodos_ordenados,
            value=(periodos_ordenados[0], periodos_ordenados[-1])
        )

        # Filtrar o DataFrame pelo intervalo de períodos
        df_filtrado_periodo = df_filtrado_disciplina[
            (df_filtrado_disciplina["DS_PERIODO"] >= periodo_inicio) &
            (df_filtrado_disciplina["DS_PERIODO"] <= periodo_fim) &
            (~df_filtrado_disciplina["DS_PERIODO"].str.endswith("/0"))
        ]

        # Verifica se há dados suficientes após o filtro para evitar gráficos vazios
        if not df_filtrado_periodo.empty:
            # Gráfico 1: Barra empilhada de aprovações e reprovações
            st.subheader("Aprovações e Reprovações por período")
            # Contar aprovações e reprovações
            df_filtrado_periodo["Aprovado"] = df_filtrado_periodo["DS_SITUACAO_DETALHADA"].apply(lambda x: 1 if x == "Aprovado" else 0)
            df_filtrado_periodo["Reprovado"] = df_filtrado_periodo["DS_SITUACAO_DETALHADA"].apply(lambda x: 1 if x != "Aprovado" else 0)

            # Agrupar por período e calcular totais de aprovados e reprovados
            df_aprov_reprov = df_filtrado_periodo.groupby("DS_PERIODO")[["Aprovado", "Reprovado"]].sum()

            if not df_aprov_reprov.empty:
                st.bar_chart(df_aprov_reprov, color=["#0000FF","#FF0000"])
            else:
                st.warning("Sem dados de aprovação/reprovação disponíveis para os períodos selecionados.")

            # Gráfico 2: Gráfico de linha com média do desempenho
            st.subheader("Média de Desempenho por período")
            df_filtrado_periodo["VL_GRAU_DISCIPLINA"] = pd.to_numeric(df_filtrado_periodo["VL_GRAU_DISCIPLINA"], errors="coerce")
            media_desempenho = df_filtrado_periodo.groupby("DS_PERIODO")["VL_GRAU_DISCIPLINA"].mean()
            media_desempenho_df = media_desempenho.reset_index(name="Média do Desempenho")

            if not media_desempenho_df.empty:
                st.line_chart(media_desempenho_df.set_index("DS_PERIODO"))
            else:
                st.warning("Sem dados de desempenho disponíveis para os períodos selecionados.")

            # Gráfico 3: Gráfico de linha com moda do desempenho
            st.subheader("Moda de Desempenho por período")
            moda_desempenho = df_filtrado_periodo.groupby("DS_PERIODO")["VL_GRAU_DISCIPLINA"].agg(lambda x: x.mode()[0] if not x.mode().empty else np.nan)
            moda_desempenho_df = moda_desempenho.reset_index(name="Moda do Desempenho")

            if not moda_desempenho_df.empty:
                st.line_chart(moda_desempenho_df.set_index("DS_PERIODO"))
            else:
                st.warning("Sem dados de moda de desempenho disponíveis para os períodos selecionados.")
        else:
            st.warning("Sem dados disponíveis para o intervalo de períodos selecionado.")
    else:
        st.info("Por favor, selecione uma disciplina para visualizar os gráficos.")

main()