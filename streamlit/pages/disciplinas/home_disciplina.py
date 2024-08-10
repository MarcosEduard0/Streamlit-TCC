import streamlit as st
import pandas as pd
import altair as alt

# Dados
data = {
    'Disciplina': [
        'Machine Learning', 'Computacao 1', 'Computacao 2', 'Inteligência Artificial', 
        'Computadores e Sociedade', 'Machine Learning', 'Computacao 1', 'Computacao 2', 
        'Inteligência Artificial', 'Computadores e Sociedade'
    ],
    'Professor': [
        'Prof. A', 'Prof. B', 'Prof. C', 'Prof. D', 'Prof. A', 
        'Prof. E', 'Prof. F', 'Prof. G', 'Prof. H', 'Prof. I'
    ],
    'Índice de Reprovação': [0.4, 0.2, 0.5, 0.3, 0.1, 0.3, 0.4, 0.6, 0.2, 0.4],
    'Índice de Aprovação': [0.6, 0.8, 0.5, 0.7, 0.9, 0.7, 0.6, 0.4, 0.8, 0.6],
    'Número de Alunos': [30, 25, 20, 40, 35, 25, 20, 30, 45, 40],
    'Nota': [7.5, 8.0, 6.0, 7.0, 9.0, 8.0, 7.0, 5.0, 8.5, 6.5],
    'Período': ['2021/1', '2021/1', '2021/1', '2022/1', '2022/2', '2022/1', '2022/1', '2021/2', '2022/2', '2021/2'],
    'Trancamentos': [2, 1, 3, 2, 0, 1, 2, 3, 1, 2],
    'Aluno': ['João', 'Pedro', 'João', 'Paula', 'Maria', 'Ana', 'Carlos', 'José', 'Clara', 'Lucas']
}

df = pd.DataFrame(data)


# Adiciona um slider para selecionar o intervalo de períodos
st.sidebar.subheader('Filtro de Período')
periodos = sorted(df['Período'].unique())
periodo_min, periodo_max = st.sidebar.select_slider(
    'Selecione o intervalo de período:',
    options=periodos,
    value=(periodos[0], periodos[-1])
)

# Filtra o dataframe de acordo com o intervalo de períodos selecionado
df_filtrado = df[(df['Período'] >= periodo_min) & (df['Período'] <= periodo_max)]

# Gráficos de colunas: Disciplinas com maior índice de aprovação e reprovação
df_aprovacao = df_filtrado.groupby('Disciplina')['Índice de Aprovação'].mean().reset_index()
df_aprovacao['Índice de Aprovação'] = df_aprovacao['Índice de Aprovação'] * 100  # Convertendo para porcentagem
df_aprovacao = df_aprovacao.sort_values(by='Índice de Aprovação', ascending=False)

df_reprovacao = df_filtrado.groupby('Disciplina')['Índice de Reprovação'].mean().reset_index()
df_reprovacao['Índice de Reprovação'] = df_reprovacao['Índice de Reprovação'] * 100  # Convertendo para porcentagem
df_reprovacao = df_reprovacao.sort_values(by='Índice de Reprovação', ascending=False)


st.subheader('Taxa de Aprovação por Disciplina (%)')
bar_chart_aprovacao = alt.Chart(df_aprovacao).mark_bar().encode(
    x=alt.X('Disciplina', sort='-y', axis=alt.Axis(labelAngle=315, labelFontSize=10)),
    y='Índice de Aprovação'
).properties(
    title=''
)
st.altair_chart(bar_chart_aprovacao, use_container_width=True)

st.subheader('Taxa de Reprovação por Disciplina (%)')
bar_chart_reprovacao = alt.Chart(df_reprovacao).mark_bar().encode(
    x=alt.X('Disciplina', sort='-y', axis=alt.Axis(labelAngle=315, labelFontSize=10)),
    y='Índice de Reprovação'
).properties(
    title=''
)
st.altair_chart(bar_chart_reprovacao, use_container_width=True)
