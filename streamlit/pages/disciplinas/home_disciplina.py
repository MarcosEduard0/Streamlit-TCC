import streamlit as st
import pandas as pd
import altair as alt

from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)

def ordenar_periodos(periodos):
    # Separar ano e semestre para ordenar
    periodos_ordenados = sorted(periodos, key=lambda x: (int(x.split("/")[0]), int(x.split("/")[1])))
    return periodos_ordenados

def main():
    # Carregamento dos dados
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

    # Ordenar os períodos de forma cronológica
    periodos_unicos = df_desempenho_academico["DS_PERIODO"].unique()
    periodos_ordenados = ordenar_periodos(periodos_unicos)

    # Filtrar por período letivo
    periodo_letivo = st.selectbox(
        "Selecione o período letivo",
        options=periodos_ordenados,
        index=periodos_ordenados.index("2019/1")
    )

    # Filtrar dados para o período selecionado
    df_filtrado = df_desempenho_academico[df_desempenho_academico["DS_PERIODO"] == periodo_letivo]

    # Filtrar apenas os aprovados
    df_aprovados = df_filtrado[df_filtrado["DS_SITUACAO_DETALHADA"] == "Aprovado"]

    # Calcular a taxa de aprovações por disciplina
    aprovacao_por_disciplina = df_aprovados.groupby("DS_NOME_DISCIPLINA").size().reset_index(name="Quantidade de Aprovados")

    # Ordenar os dados da maior para a menor quantidade de aprovados
    aprovacao_por_disciplina = aprovacao_por_disciplina.sort_values(by="Quantidade de Aprovados", ascending=False)

    # Limitar para mostrar apenas as 10 disciplinas com mais aprovações
    top_10_aprovacao = aprovacao_por_disciplina.head(10)

    # Criar gráfico de barras
    grafico_aprovacao = alt.Chart(top_10_aprovacao).mark_bar().encode(
        x=alt.X("DS_NOME_DISCIPLINA:N", title="Disciplina", sort="-y", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Quantidade de Aprovados:Q", title="Quantidade de Aprovados"),
        tooltip=["DS_NOME_DISCIPLINA", "Quantidade de Aprovados"]
    ).properties(
        width=800, 
        height=400,
        title=f"Top 10 Taxa de Aprovação por Disciplina - Período {periodo_letivo}"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_view(
        continuousWidth=800, 
        continuousHeight=400
    )

    st.altair_chart(grafico_aprovacao, use_container_width=True)

    # Filtrar apenas os reprovados (situações diferentes de "Aprovado")
    df_reprovados = df_filtrado[df_filtrado["DS_SITUACAO_DETALHADA"] != "Aprovado"]

    # Calcular a quantidade de reprovações por disciplina
    reprovacao_por_disciplina = df_reprovados.groupby("DS_NOME_DISCIPLINA").size().reset_index(name="Quantidade de Reprovados")

    # Ordenar os dados da maior para a menor quantidade de reprovados
    reprovacao_por_disciplina = reprovacao_por_disciplina.sort_values(by="Quantidade de Reprovados", ascending=False)

    # Limitar para mostrar apenas as 10 disciplinas com mais reprovações
    top_10_reprovacao = reprovacao_por_disciplina.head(10)

    # Criar gráfico de barras para reprovações
    grafico_reprovacao = alt.Chart(top_10_reprovacao).mark_bar().encode(
        x=alt.X("DS_NOME_DISCIPLINA:N", title="Disciplina", sort="-y", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Quantidade de Reprovados:Q", title="Quantidade de Reprovados"),
        tooltip=["DS_NOME_DISCIPLINA", "Quantidade de Reprovados"]
    ).properties(
        width=800, 
        height=400,
        title=f"Top 10 Taxa de Reprovação por Disciplina - Período {periodo_letivo}"
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_view(
        continuousWidth=800, 
        continuousHeight=400
    )

    st.altair_chart(grafico_reprovacao, use_container_width=True)

main()