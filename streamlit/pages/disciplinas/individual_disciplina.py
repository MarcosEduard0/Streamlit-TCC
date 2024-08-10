import streamlit as st
import pandas as pd
import plotly.express as px

# Dados
data = {
    "Disciplina": [
        "Machine Learning",
        "Computacao 1",
        "Computacao 2",
        "Inteligência Artificial",
        "Computadores e Sociedade",
        "Machine Learning",
        "Computacao 1",
        "Computacao 2",
        "Inteligência Artificial",
        "Computadores e Sociedade",
    ],
    "Professor": [
        "Prof. A",
        "Prof. B",
        "Prof. C",
        "Prof. D",
        "Prof. A",
        "Prof. E",
        "Prof. F",
        "Prof. G",
        "Prof. H",
        "Prof. I",
    ],
    "Índice de Reprovação": [0.4, 0.2, 0.5, 0.3, 0.1, 0.3, 0.4, 0.6, 0.2, 0.4],
    "Índice de Aprovação": [0.6, 0.8, 0.5, 0.7, 0.9, 0.7, 0.6, 0.4, 0.8, 0.6],
    "Número de Alunos": [30, 25, 20, 40, 35, 25, 20, 30, 45, 40],
    "Nota": [7.5, 8.0, 6.0, 7.0, 9.0, 8.0, 7.0, 5.0, 8.5, 6.5],
    "Período": [
        "2021/1",
        "2021/1",
        "2021/1",
        "2022/1",
        "2022/2",
        "2022/1",
        "2022/1",
        "2021/2",
        "2022/2",
        "2021/2",
    ],
    "Trancamentos": [2, 1, 3, 2, 0, 1, 2, 3, 1, 2],
    "Aluno": [
        "João",
        "Pedro",
        "João",
        "Paula",
        "Maria",
        "Ana",
        "Carlos",
        "José",
        "Clara",
        "Lucas",
    ],
}

df = pd.DataFrame(data)

st.title("Análise de Disciplinas")

# Lista de disciplinas únicas para o autocomplete
lista_disciplinas = df["Disciplina"].unique()

# Filtro para a disciplina com autocomplete
disciplina_selecionada = st.selectbox(
    "Selecione a disciplina que deseja filtrar:", options=lista_disciplinas, index=0
)

# Filtrando a disciplina selecionada
df_filtrado = df[df["Disciplina"] == disciplina_selecionada]

# Gráfico de linhas: Média de notas por semestre
st.subheader("Média de Notas por Semestre")
df_semestre_media = df_filtrado.groupby("Período")["Nota"].mean().reset_index()

fig_linhas = px.line(
    df_semestre_media,
    x="Período",
    y="Nota",
    title="Média de Notas por Semestre",
    markers=True,
)
st.plotly_chart(fig_linhas)

# Gráfico de colunas: Disciplinas com maior índice de reprovação (em %)
st.subheader("Disciplinas com Maior Índice de Reprovação")
df_reprovacao = df.groupby("Disciplina")["Índice de Reprovação"].mean().reset_index()
df_reprovacao["Índice de Reprovação"] = (
    df_reprovacao["Índice de Reprovação"] * 100
)  # Convertendo para porcentagem
df_reprovacao = df_reprovacao.sort_values(by="Índice de Reprovação", ascending=False)

# Formatando o texto com duas casas decimais
fig_reprovacao = px.bar(
    df_reprovacao,
    x="Disciplina",
    y="Índice de Reprovação",
    title="Índice de Reprovação por Disciplina (%)",
    text=df_reprovacao["Índice de Reprovação"].apply(lambda x: f"{x:.2f}%"),
)
fig_reprovacao.update_layout(yaxis_title="Índice de Reprovação (%)")
st.plotly_chart(fig_reprovacao)

# Gráfico de colunas: Disciplinas com maior índice de aprovação (em %)
st.subheader("Disciplinas com Maior Índice de Aprovação")
df_aprovacao = df.groupby("Disciplina")["Índice de Aprovação"].mean().reset_index()
df_aprovacao["Índice de Aprovação"] = (
    df_aprovacao["Índice de Aprovação"] * 100
)  # Convertendo para porcentagem
df_aprovacao = df_aprovacao.sort_values(by="Índice de Aprovação", ascending=False)

# Formatando o texto com duas casas decimais
fig_aprovacao = px.bar(
    df_aprovacao,
    x="Disciplina",
    y="Índice de Aprovação",
    title="Índice de Aprovação por Disciplina (%)",
    text=df_aprovacao["Índice de Aprovação"].apply(lambda x: f"{x:.2f}%"),
)
fig_aprovacao.update_layout(yaxis_title="Índice de Aprovação (%)")
st.plotly_chart(fig_aprovacao)

# Gráfico de colunas: Número de alunos que cursaram determinada disciplina por semestre
st.subheader(f"Número de Alunos que Cursaram a Disciplina: {disciplina_selecionada}")
df_num_alunos = df_filtrado.groupby("Período")["Número de Alunos"].sum().reset_index()

fig_num_alunos = px.bar(
    df_num_alunos,
    x="Período",
    y="Número de Alunos",
    title=f"Número de Alunos por Semestre para {disciplina_selecionada}",
    text="Número de Alunos",
)
st.plotly_chart(fig_num_alunos)

# Gráfico de colunas: Média de nota dos alunos em determinada disciplina por semestre
st.subheader(f"Média de Nota dos Alunos em {disciplina_selecionada}")
df_media_nota = df_filtrado.groupby("Período")["Nota"].mean().reset_index()

fig_media_nota = px.bar(
    df_media_nota,
    x="Período",
    y="Nota",
    title=f"Média de Nota por Semestre para {disciplina_selecionada}",
    text="Nota",
)
st.plotly_chart(fig_media_nota)

# Gráfico de colunas: Moda de nota dos alunos em determinada disciplina por semestre
st.subheader(f"Moda de Nota dos Alunos em {disciplina_selecionada}")
df_moda_nota = (
    df_filtrado.groupby("Período")["Nota"]
    .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    .reset_index()
)

fig_moda_nota = px.bar(
    df_moda_nota,
    x="Período",
    y="Nota",
    title=f"Moda de Nota por Semestre para {disciplina_selecionada}",
    text="Nota",
)
st.plotly_chart(fig_moda_nota)

# Gráfico de colunas: Disciplinas com maior índice de trancamentos por semestre
st.subheader("Quantidade de Trancamentos por Semestre")
df_trancamentos = df_filtrado.groupby("Período")["Trancamentos"].sum().reset_index()

fig_trancamentos = px.bar(
    df_trancamentos,
    x="Período",
    y="Trancamentos",
    title=f"Trancamentos por Semestre para {disciplina_selecionada}",
    text="Trancamentos",
)
st.plotly_chart(fig_trancamentos)
