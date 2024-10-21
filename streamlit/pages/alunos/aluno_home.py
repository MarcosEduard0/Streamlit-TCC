import streamlit as st
import pandas as pd
import plotly.express as px


from utils.auxiliary_functions.all_auxiliary_functions import (
    carregar_dados,
    merge_dataframes,
)

# -----------------------------------------------------------
# Script de Criação da Interface Streamlit para página inicial de Alunos
# Autor: Marcos Eduardo
# Data de Criação:
# Descrição: Este script cria uma interface Streamlit para exibir e filtrar
# dados dos alunos, incluindo opções de pesquisa por nome ou matrícula,
# seleção por situação de matrícula, modalidade de cota e intervalo de CR acumulado.
# -----------------------------------------------------------


# Função para aplicar a regra 1: Periodo maior que 14
def obter_alunos_tipo_1(df_aluno):
    df_alunos_tipo_1 = df_aluno[df_aluno["VL_PERIODOS_INTEGRALIZADOS"] > 14][
        [
            "DS_MATRICULA_DRE",
            "NM_ALUNO",
            "DS_PERIODO_INGRESSO_UFRJ",
            "DS_MODALIDADE_COTA",
            "DS_SITUACAO",
        ]
    ].reset_index(drop=True)
    df_alunos_tipo_1["TIPO_RISCO"] = "1️⃣"
    return df_alunos_tipo_1


# Função para identificar alunos com 3 períodos consecutivos com VL_CR_ACUMULADO < 3
def filtra_alunos_consecutivos(df_aluno_ativos):
    df = df_aluno_ativos.sort_values(by="DS_PERIODO", ascending=False)

    # Verifica se existem pelo menos 3 períodos
    if len(df) < 3:
        return pd.DataFrame(columns=df_aluno_ativos.columns).dropna(
            axis=1, how="all"
        )  # Remove colunas com todos NaN

    # Seleciona os três últimos períodos
    df_ultimos_periodos = df.head(3)

    # Verifica se os três últimos VL_CR_ACUMULADO são menores que 3
    if (df_ultimos_periodos["VL_CR_ACUMULADO"] < 3).all():
        return df_ultimos_periodos
    else:
        return pd.DataFrame(columns=df_aluno_ativos.columns).dropna(axis=1, how="all")


# Função para aplicar a regra 2: CRA menor que 3 consecutivos
def obter_alunos_tipo_2(df_aluno_ativos, df_situacao_periodo):
    df_situacao_periodo = df_situacao_periodo[
        ["SK_D_ALUNO", "VL_CR_PERIODO", "VL_CR_ACUMULADO", "DS_PERIODO"]
    ]

    #  Faz o merge dos DataFrames
    df_aluno_ativos = df_situacao_periodo.merge(
        df_aluno_ativos,
        on="SK_D_ALUNO",
        how="inner",
    )

    # Aplica a filtragem por consecutividade
    df_alunos_tipo_2 = (
        df_aluno_ativos.groupby("DS_MATRICULA_DRE")
        .apply(filtra_alunos_consecutivos)
        .reset_index(drop=True)
    )

    # Verifica se o DataFrame não está vazio
    if not df_alunos_tipo_2.empty:
        df_alunos_tipo_2 = (
            df_alunos_tipo_2[
                [
                    "DS_MATRICULA_DRE",
                    "NM_ALUNO",
                    "DS_PERIODO_INGRESSO_UFRJ",
                    "DS_MODALIDADE_COTA",
                    "DS_SITUACAO",
                ]
            ]
            .drop_duplicates()
            .reset_index(drop=True)
        )

        df_alunos_tipo_2["TIPO_RISCO"] = "2️⃣"

    return df_alunos_tipo_2


# Função principal para processar os dados de alunos ativos
def processa_alunos_ativos(df_situacao_matricula):
    df_aluno_ativos = df_situacao_matricula[
        [
            "SK_D_ALUNO",
            "DS_MATRICULA_DRE",
            "NM_ALUNO",
            "VL_PERIODOS_INTEGRALIZADOS",
            "DS_PERIODO_INGRESSO_UFRJ",
            "DS_MODALIDADE_COTA",
            "DS_PERIODO",
            "DS_SITUACAO",
        ]
    ]
    df_aluno_ativos = df_aluno_ativos.sort_values(
        by=["DS_MATRICULA_DRE", "DS_PERIODO"], ascending=[True, False]
    ).drop("DS_PERIODO", axis=1)

    df_aluno_ativos = df_aluno_ativos.drop_duplicates(
        subset="DS_MATRICULA_DRE", keep="first"
    )

    df_aluno_ativos = df_aluno_ativos[
        df_aluno_ativos["DS_SITUACAO"].isin(["Ativa", "Trancada"])
    ]

    return df_aluno_ativos


def obter_alunos_tipo_3(df_aluno_ativos, df_desempenho_academico):
    # Filtra alunos que não foram aprovados
    df_reprovacoes = df_desempenho_academico[
        df_desempenho_academico["DS_SITUACAO_DETALHADA"] != "Aprovado"
    ][["SK_D_ALUNO", "SK_D_DISCIPLINA", "DS_SITUACAO"]]

    # Realiza o merge com alunos ativos
    df_reprovacoes = df_reprovacoes.merge(
        df_aluno_ativos,
        on="SK_D_ALUNO",
        how="inner",
        suffixes=("_DISCIPLINA", "_MATRICULA"),
    )

    # Agrupa as reprovações por aluno e disciplina, contando a quantidade de reprovações
    reprovacao_agg = (
        df_reprovacoes.groupby(
            [
                "SK_D_DISCIPLINA",
                "DS_MATRICULA_DRE",
                "NM_ALUNO",
                "DS_MODALIDADE_COTA",
                "DS_PERIODO_INGRESSO_UFRJ",
                "DS_SITUACAO_MATRICULA",
            ]
        )
        .size()
        .reset_index(name="QUANTIDADE_REPRO")
        .sort_values("QUANTIDADE_REPRO", ascending=False)
    )

    # Filtra alunos com mais de 3 reprovações na mesma disciplina
    df_alunos_tipo_3 = reprovacao_agg[reprovacao_agg["QUANTIDADE_REPRO"] > 3]

    # Remove colunas desnecessárias e duplicatas
    df_alunos_tipo_3 = (
        df_alunos_tipo_3.drop(["SK_D_DISCIPLINA", "QUANTIDADE_REPRO"], axis=1)
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # Renomeia a coluna 'DS_SITUACAO_MATRICULA' para 'DS_SITUACAO'
    df_alunos_tipo_3 = df_alunos_tipo_3.rename(
        columns={"DS_SITUACAO_MATRICULA": "DS_SITUACAO"}
    )

    # Adiciona a regra correspondente
    df_alunos_tipo_3["TIPO_RISCO"] = "3️⃣"

    return df_alunos_tipo_3


def gerar_tabela_alunos_em_risco(df_alunos_em_risco):
    # Agrupa alunos com múltiplos tipos de risco, combinando os valores em uma lista
    df_alunos_em_risco = (
        df_alunos_em_risco.groupby(
            [
                "DS_MATRICULA_DRE",
                "NM_ALUNO",
                "DS_MODALIDADE_COTA",
                "DS_PERIODO_INGRESSO_UFRJ",
                "DS_SITUACAO",
            ]
        )
        .agg({"TIPO_RISCO": lambda tipos: ", ".join(map(str, sorted(set(tipos))))})
        .reset_index()
    )

    # Cria um link a partir do DRE do aluno
    df_alunos_em_risco["DS_MATRICULA_DRE"] = df_alunos_em_risco[
        "DS_MATRICULA_DRE"
    ].apply(lambda dre: f"aluno_individual?dre={dre}")

    # Configuração do dataframe para exibir alunos em risco
    st.dataframe(
        df_alunos_em_risco,
        use_container_width=True,
        selection_mode=["single-row"],
        column_config={
            "DS_MATRICULA_DRE": st.column_config.LinkColumn(
                "Matrícula DRE",
                display_text="aluno_individual\\?dre=([^&\\s]*)",
            ),
            "NM_ALUNO": "Nome Completo",
            "DS_MODALIDADE_COTA": "Tipo de Cota",
            "DS_PERIODO_INGRESSO_UFRJ": "Período de Ingresso na UFRJ",
            "DS_SITUACAO": "Situação da Matrícula",
            "TIPO_RISCO": "Tipos de Riscos",
        },
        hide_index=True,
    )

    # Legenda explicando os critérios de risco
    with st.expander("Ver descrição"):
        st.write(
            """
            Os critérios para que um aluno seja considerado em situação de risco são os seguintes:
            - **Tipo 1**: Períodos integralizados superior a 14.
            - **Tipo 2**: Três CRA consecutivos menores que 3.
            - **Tipo 3**: Quatro reprovações em uma mesma disciplina.
            """
        )


def grafico_situacao_matricula_periodo(dataframe):
    data = dataframe[dataframe["DS_SITUACAO"] != "Ativa"]
    data = (
        data.groupby(["DS_SITUACAO", "DS_PERIODO"])
        .size()
        .reset_index(name="quantidade")
    )

    data.sort_values("DS_PERIODO", inplace=True)

    fig = px.bar(
        data,
        x="DS_PERIODO",
        y="quantidade",
        color="DS_SITUACAO",
        labels={
            "quantidade": "Quantidade",
            "DS_PERIODO": "Período",
            "DS_SITUACAO": "Situação da Matrícula",
        },
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(title="Situação da Matrícula", traceorder="normal"),
        barmode="stack",
    )
    st.plotly_chart(fig)


def grafico_media_cra_periodo(dataframe):

    data = (
        dataframe.groupby(["DS_PERIODO"])["VL_CR_ACUMULADO"]
        .mean()
        .reset_index(name="media")
    )
    data["media"] = data["media"].round(2)
    data.sort_values("DS_PERIODO", inplace=True)

    fig = px.line(
        data,
        x="DS_PERIODO",
        y="media",
        labels={"media": "Média CRA", "DS_PERIODO": "Período"},
        markers=True,
    )

    st.plotly_chart(fig)


def grafico_situacao_matricula_periodo_ingresso(df_situacao_matricula):

    # Ordenar o dataframe pelo período em ordem decrescente para que o mais recente venha primeiro
    df_situacao_matricula = df_situacao_matricula.sort_values(
        ["DS_MATRICULA_DRE", "DS_PERIODO"], ascending=False
    )

    # Remover duplicatas mantendo apenas o registro mais recente para cada aluno (considerando a coluna de situação)
    dataframe = df_situacao_matricula.drop_duplicates(
        subset=["DS_MATRICULA_DRE"], keep="first"
    )

    data = (
        dataframe.groupby(["DS_SITUACAO", "DS_PERIODO_INGRESSO_UFRJ"])
        .size()
        .reset_index(name="quantidade")
    )

    data.sort_values("DS_PERIODO_INGRESSO_UFRJ", inplace=True)

    # Calcula o total de cada período de ingresso
    total_por_periodo = (
        data.groupby("DS_PERIODO_INGRESSO_UFRJ")["quantidade"]
        .sum()
        .reset_index(name="total")
    )

    # Junta os totais ao dataframe original
    data = data.merge(total_por_periodo, on="DS_PERIODO_INGRESSO_UFRJ")

    fig = px.bar(
        data,
        x="DS_PERIODO_INGRESSO_UFRJ",
        y="quantidade",
        color="DS_SITUACAO",
        labels={
            "quantidade": "Quantidade",
            "DS_PERIODO_INGRESSO_UFRJ": "Período de Ingresso na UFRJ",
            "DS_SITUACAO": "Situação da Matrícula",
        },
    )

    # Customiza o hovertemplate para incluir o total
    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "Período de Ingresso: %{x}",
                "Quantidade: %{y}",
                "Total no Período: %{customdata[0]}",
            ]
        ),
        customdata=data[["total"]].values,
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(title="Situação da Matrícula", traceorder="normal"),
        barmode="stack",
    )

    st.plotly_chart(fig)


def periodos_anteriores(periodo_atual, num_semestres):
    ano, semestre = periodo_atual.split("/")
    ano = int(ano)
    semestre = int(semestre)

    total_semestres = (ano * 2 + semestre) - num_semestres

    ano_anterior = total_semestres // 2
    semestre_anterior = total_semestres % 2

    if semestre_anterior == 0:
        semestre_anterior = 2
        ano_anterior -= 1

    return f"{ano_anterior}/{semestre_anterior}"


def aplicar_filtros(
    df,
    inicio_periodo,
    fim_periodo,
    sexo,
    modalidade,
    nome_coluna_periodo="DS_PERIODO_INGRESSO_UFRJ",
):
    # Aplicando filtro de intervalo de periodo
    df_filtrado = df[
        (df[nome_coluna_periodo] >= inicio_periodo)
        & (df[nome_coluna_periodo] <= fim_periodo)
    ]
    # Aplicar filtro de sexo, se houver seleção
    if sexo:
        df_filtrado = df_filtrado[df_filtrado["DS_SEXO"].isin(sexo)]

    # Aplicar filtro de modalidade de cota, se houver seleção
    if modalidade:
        df_filtrado = df_filtrado[df_filtrado["DS_MODALIDADE_COTA"].isin(modalidade)]

    return df_filtrado


def main():
    # Carregamento dos dados
    dados = carregar_dados(
        datasets=[
            "d_aluno",
            "d_curso",
            "d_periodo",
            "d_situacao",
            "f_matricula_aluno",
            "f_situacao_periodo",
            "f_desempenho_academico",
        ]
    )

    # Criar tabela Fato Matricula Aluno
    dimensions = [dados.get("d_periodo"), dados.get("d_aluno"), dados.get("d_situacao")]
    df_situacao_matricula = merge_dataframes(dimensions, dados.get("f_matricula_aluno"))

    # Criar tabela Fato Situação Período
    df_situacao_periodo = merge_dataframes(
        [dados.get("d_periodo"), dados.get("d_aluno")], dados.get("f_situacao_periodo")
    )

    # Fato Desemepnho Academico
    dimensions = [dados.get("d_periodo"), dados.get("d_situacao")]
    df_desempenho_academico = merge_dataframes(
        dimensions, dados.get("f_desempenho_academico")
    )

    # Informações iniciais da Pagina
    st.header("Sistema de Análises Acadêmica 🎓")
    st.subheader("Dados Gerais de Alunos")

    # Barra de Filtros
    with st.sidebar:
        # Obtenção das listas de opções
        lista_periodos = dados.get("d_periodo")["DS_PERIODO"]
        lista_cotas = dados.get("d_aluno")["DS_MODALIDADE_COTA"].unique()
        lista_sexo = ["Masculino", "Feminino"]

        # Filtra a lista de períodos para remover os que terminam com "/0" ou "/3"
        lista_periodos_filtrada = lista_periodos[
            ~lista_periodos.str.endswith(("/0", "/3"))
        ].to_list()

        # Slider para selecionar o período de ingresso
        inicio_periodo_UFRJ, fim_periodo_UFRJ = st.select_slider(
            label="Período",
            options=lista_periodos_filtrada,
            value=(min(lista_periodos_filtrada), max(lista_periodos_filtrada)),
        )

        # Multiselect para selecionar o sexo
        sexo_selecionado = st.multiselect(
            label="Sexo",
            options=lista_sexo,
            placeholder="Selecione as opções",
        )

        # Multiselect para selecionar a modalidade de cota
        modalidade_selecionada = st.multiselect(
            label="Modalidade de Cota",
            options=lista_cotas,
            placeholder="Selecione as opções",
        )

        df_situacao_matricula_filtrado = aplicar_filtros(
            df_situacao_matricula,
            inicio_periodo_UFRJ,
            fim_periodo_UFRJ,
            sexo_selecionado,
            modalidade_selecionada,
        )

        df_situacao_matricula_CR_filtrado = aplicar_filtros(
            df_situacao_matricula,
            inicio_periodo_UFRJ,
            fim_periodo_UFRJ,
            sexo_selecionado,
            modalidade_selecionada,
            "DS_PERIODO",
        )
        df_situacao_periodo_filtrado = aplicar_filtros(
            df_situacao_periodo,
            inicio_periodo_UFRJ,
            fim_periodo_UFRJ,
            sexo_selecionado,
            modalidade_selecionada,
            "DS_PERIODO",
        )

        d_aluno_filtrado = aplicar_filtros(
            dados.get("d_aluno"),
            inicio_periodo_UFRJ,
            fim_periodo_UFRJ,
            sexo_selecionado,
            modalidade_selecionada,
        )

        st.button("Limpar")

    # Primeiro container
    with st.container():
        col1, col2 = st.columns(2)
        total_alunos = len(d_aluno_filtrado)
        col1.metric("Total de Alunos por Ingresso", total_alunos, 1)
        col2.metric("Idade Média de Formação", 25)

        st.divider()

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Situação de Matricula por Período")
            grafico_situacao_matricula_periodo(df_situacao_matricula_CR_filtrado)

        with col2:
            st.subheader("Média CRA por Perído")
            grafico_media_cra_periodo(df_situacao_periodo_filtrado)
        st.divider()

    # Segundo container
    with st.container():
        st.subheader("Alunos em Situação de Risco")

        # Processamento dos alunos ativos
        df_aluno_ativos = processa_alunos_ativos(df_situacao_matricula_filtrado)

        # Aplica a Regra 1
        df_alunos_tipo_1 = obter_alunos_tipo_1(df_aluno_ativos)

        # Aplica a Regra 2
        df_alunos_tipo_2 = obter_alunos_tipo_2(df_aluno_ativos, df_situacao_periodo)

        df_alunos_tipo_3 = obter_alunos_tipo_3(df_aluno_ativos, df_desempenho_academico)
        # Concatena os três tipos de alunos em risco
        df_alunos_em_risco = pd.concat(
            [df_alunos_tipo_1, df_alunos_tipo_2, df_alunos_tipo_3], axis=0
        )
        gerar_tabela_alunos_em_risco(df_alunos_em_risco)

    # Segundo container
    with st.container():
        st.subheader("Situação de Matricula por Periodo de Ingresso")
        grafico_situacao_matricula_periodo_ingresso(df_situacao_matricula_filtrado)
        st.divider()

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Concentração de Alunos por Bairro")

            df_aluno_mapa = (
                d_aluno_filtrado[
                    ["DS_BAIRRO", "DS_ESTADO", "VL_LATITUDE", "VL_LONGITUDE"]
                ]
                .groupby(["DS_BAIRRO", "DS_ESTADO", "VL_LATITUDE", "VL_LONGITUDE"])
                .size()
                .reset_index(name="Total")
                .rename(columns={"DS_BAIRRO": "Bairro"})  # Renomeando para 'Bairro'
            )

            fig = px.scatter_mapbox(
                df_aluno_mapa,
                lat="VL_LATITUDE",
                lon="VL_LONGITUDE",
                color="Total",
                size="Total",
                color_continuous_scale=px.colors.cyclical.IceFire,
                mapbox_style="carto-positron",
                size_max=15,
                zoom=10,
                hover_data={
                    "Bairro": True,
                    "Total": True,
                    "VL_LATITUDE": False,
                    "VL_LONGITUDE": False,
                },
            )
            st.plotly_chart(fig)

        with col2:
            st.subheader("Tempo até se formação")

            # Filtrar alunos com a situação "Concluído"
            df_formandos = df_situacao_matricula_filtrado[
                df_situacao_matricula_filtrado["DS_SITUACAO"] == "Concluido"
            ].copy()

            # Extrair anos de ingresso e término
            df_formandos["ANO_INGRESSO"] = (
                df_formandos["DS_PERIODO_INGRESSO_UFRJ"]
                .str.split("/")
                .str[0]
                .astype(int)
            )
            df_formandos["ANO_TERMINO"] = (
                df_formandos["DS_PERIODO"].str.split("/").str[0].astype(int)
            )

            # Calcular a idade de formação
            df_formandos["DS_IDADE_FORMACAO"] = (
                df_formandos["ANO_TERMINO"] - df_formandos["ANO_INGRESSO"]
            )

            # Criar gráfico do tipo violino
            fig = px.violin(
                df_formandos,
                y="DS_IDADE_FORMACAO",
                color="DS_SEXO",
                # violinmode="overlay",
                points="all",
                box=True,
                labels={"DS_IDADE_FORMACAO": "Anos para Formação", "DS_SEXO": "Sexo"},
            )

            # Atualizar o título do eixo Y
            fig.update_layout(yaxis_title="Duração em Anos")

            st.plotly_chart(fig)

        st.divider()


main()
