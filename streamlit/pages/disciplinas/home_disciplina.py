import streamlit as st
import pandas as pd
import altair as alt

from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)

st.markdown("# Disciplinas")

def ordenar_periodos(periodos):
    # Separar ano e semestre para ordenar em ordem decrescente
    periodos_ordenados = sorted(periodos, key=lambda x: (int(x.split("/")[0]), int(x.split("/")[1])), reverse=True)
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
    # FILTRO DE PERÍODO
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
    
    # APROVADOS - DATAFRAME
    # Filtrar apenas os aprovados
    df_aprovados = df_filtrado[df_filtrado["DS_SITUACAO_DETALHADA"] == "Aprovado"]
    # Calcular a taxa de aprovações por disciplina
    aprovados_por_disciplina = df_aprovados.groupby("DS_NOME_DISCIPLINA").size().reset_index(name="Quantidade de Aprovados")
    
    # REPROVADOS - DATAFRAME
    # Filtrar apenas os reprovados (situações diferentes de "Aprovado")
    df_reprovados = df_filtrado[df_filtrado["DS_SITUACAO_DETALHADA"] != "Aprovado"]
    # Calcular a quantidade de reprovações por disciplina
    reprovados_por_disciplina = df_reprovados.groupby("DS_NOME_DISCIPLINA").size().reset_index(name="Quantidade de Reprovados")

    # GRÁFICO 1 - TAXA DE APROVAÇÃO POR DISCIPLINA
    # Mesclar os dois dataframes para obter a taxa de aprovação por disciplina
    taxa_aprovacao = pd.merge(aprovados_por_disciplina, reprovados_por_disciplina, on='DS_NOME_DISCIPLINA', how='left')
    # Calcular a taxa de aprovação
    taxa_aprovacao['Taxa de Aprovação'] = taxa_aprovacao['Quantidade de Aprovados'] / (taxa_aprovacao['Quantidade de Aprovados'] + taxa_aprovacao['Quantidade de Reprovados'])
    # Remover linhas onde a taxa de aprovação é NaN
    taxa_aprovacao = taxa_aprovacao.dropna(subset=['Taxa de Aprovação'])
    # Formatar a taxa de aprovação como porcentagem para exibição
    taxa_aprovacao['Taxa de Aprovação (%)'] = (taxa_aprovacao['Taxa de Aprovação'] * 100).apply(lambda x: f"{x:.1f}%")
    # Ordenar os dados da maior para a menor quantidade de aprovados
    taxa_aprovacao = taxa_aprovacao.sort_values(by="Taxa de Aprovação", ascending=False)
    # Limitar para mostrar as disciplinas com mais aprovações
    top_disciplinas_aprovacao = taxa_aprovacao.head(40)
    # Exibir a tabela
    st.subheader("Maiores taxas de Aprovação")
    st.dataframe(top_disciplinas_aprovacao[[
        'DS_NOME_DISCIPLINA',  
        'Taxa de Aprovação (%)', 
        'Quantidade de Aprovados', 
        'Quantidade de Reprovados']].reset_index(drop=True), 
        height=400, 
        width=900, 
        hide_index=True,
        column_config={
            "DS_NOME_DISCIPLINA" : "Disciplina",
            "Quantidade de Aprovados": "Aprovados", 
            "Quantidade de Reprovados": "Reprovados"
        })
    
    # GRÁFICO 2 - TAXA DE REPROVAÇÃO POR DISCIPLINA
    # Mesclar os dois dataframes para obter a taxa de aprovação por disciplina
    taxa_reprovacao = pd.merge(aprovados_por_disciplina, reprovados_por_disciplina, on='DS_NOME_DISCIPLINA', how='left')
    # Calcular a taxa de aprovação
    taxa_reprovacao['Taxa de Reprovação'] = taxa_reprovacao['Quantidade de Reprovados'] / (taxa_reprovacao['Quantidade de Reprovados'] + taxa_reprovacao['Quantidade de Aprovados'])
    # Remover linhas onde a taxa de reprovação é NaN
    taxa_reprovacao = taxa_reprovacao.dropna(subset=['Taxa de Reprovação'])
    # Formatar a taxa de aprovação como porcentagem para exibição
    taxa_reprovacao['Taxa de Reprovação (%)'] = (taxa_reprovacao['Taxa de Reprovação'] * 100).apply(lambda x: f"{x:.1f}%")
    # Ordenar os dados da maior para a menor quantidade de aprovados
    taxa_reprovacao = taxa_reprovacao.sort_values(by="Taxa de Reprovação", ascending=False)
    # Limitar para mostrar as disciplinas com mais reprovações
    top_disciplinas_reprovacao = taxa_reprovacao.head(40)
    # Exibir a tabela
    st.subheader("Maiores taxas de Reprovação")
    st.dataframe(top_disciplinas_reprovacao[[
        'DS_NOME_DISCIPLINA',  
        'Taxa de Reprovação (%)', 
        'Quantidade de Aprovados', 
        'Quantidade de Reprovados']].reset_index(drop=True), 
        height=400, 
        width=900, 
        hide_index=True,
        column_config={
            "DS_NOME_DISCIPLINA" : "Disciplina",
            "Quantidade de Aprovados": "Aprovados", 
            "Quantidade de Reprovados": "Reprovados"
        })

main()