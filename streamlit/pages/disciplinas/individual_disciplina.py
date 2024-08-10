import streamlit as st
import pandas as pd
import altair as alt

# Dados
data = {
    'Disciplina': [
        'Machine Learning', 'Computacao 1', 'Computacao 2', 'Inteligência Artificial', 
        'Computadores e Sociedade', 'Machine Learning', 'Computacao 1', 'Computacao 2', 
        'Inteligência Artificial', 'Computadores e Sociedade',
        'Machine Learning', 'Computacao 1', 'Computacao 2', 'Inteligência Artificial', 
        'Computadores e Sociedade', 'Machine Learning', 'Computacao 1', 'Computacao 2', 
        'Inteligência Artificial', 'Computadores e Sociedade'
    ],
    'Professor': [
        'Prof. A', 'Prof. B', 'Prof. C', 'Prof. D', 'Prof. A', 
        'Prof. E', 'Prof. F', 'Prof. G', 'Prof. H', 'Prof. I',
        'Prof. A', 'Prof. B', 'Prof. C', 'Prof. D', 'Prof. A', 
        'Prof. E', 'Prof. F', 'Prof. G', 'Prof. H', 'Prof. I'
    ],
    'Nota': [7.5, 8.0, 6.0, 7.0, 9.0, 8.0, 7.0, 5.0, 8.5, 6.5,
             7.0, 6.5, 8.5, 7.0, 8.0, 7.5, 8.0, 6.0, 7.5, 8.0],
    'Período': ['2021/1', '2021/1', '2021/1', '2022/1', '2022/2', '2022/1', '2022/1', '2021/2', '2022/2', '2021/2',
                '2023/1', '2023/1', '2023/1', '2023/2', '2023/2', '2023/2', '2024/1', '2024/1', '2024/2', '2024/2'],
    'Trancamentos': [2, 1, 3, 2, 0, 1, 2, 3, 1, 2, 1, 3, 2, 1, 2, 1, 2, 3, 1, 2],
    'Aluno': ['João', 'Pedro', 'João', 'Paula', 'Maria', 'Ana', 'Carlos', 'José', 'Clara', 'Lucas',
              'Marcos', 'Sofia', 'Gabriel', 'Fernanda', 'Ricardo', 'Bruna', 'Felipe', 'Eduarda', 'Rafael', 'Luiza']
}

df = pd.DataFrame(data)

# Adiciona o atributo de aprovação
df['Aprovação'] = df['Nota'].apply(lambda x: 'Aprovado' if x >= 7 else 'Reprovado')

# Adiciona um slider para selecionar o intervalo de períodos
st.sidebar.subheader('Filtro de Período')
periodos = sorted(df['Período'].unique())
periodo_min, periodo_max = st.sidebar.select_slider(
    'Selecione o intervalo de período:',
    options=periodos,
    value=(periodos[0], periodos[-1])
)

# Filtra o dataframe de acordo com o intervalo de períodos selecionado
df = df[(df['Período'] >= periodo_min) & (df['Período'] <= periodo_max)]

st.title('Análise de Disciplinas')

# Lista de disciplinas únicas para o autocomplete
lista_disciplinas = df['Disciplina'].unique()

# Filtro para a disciplina com autocomplete
disciplina_selecionada = st.selectbox('Selecione a disciplina que deseja filtrar:', options=lista_disciplinas, index=0)

# Filtrando a disciplina selecionada
df_filtrado = df[df['Disciplina'] == disciplina_selecionada]

# Primeiro componente: Gráfico de colunas com quantidade de aprovados e reprovados por período
st.subheader(f'Aprovações e Reprovações em {disciplina_selecionada}')
df_aprovacao = df_filtrado.groupby(['Período', 'Aprovação']).size().reset_index(name='Quantidade')

chart_aprovacao = alt.Chart(df_aprovacao).mark_bar().encode(
    x=alt.X('Período', axis=alt.Axis(labelAngle=0)),  # Rótulos do eixo X na horizontal
    y='Quantidade',
    color='Aprovação'
).properties(
    width=600,
    height=400
)

st.altair_chart(chart_aprovacao, use_container_width=True)

# Separador
st.markdown('---')

# Segundo componente: Gráficos de linhas
st.subheader(f'Notas dos Alunos em {disciplina_selecionada}')

# Média das Notas
st.subheader('Média')
df_media_nota = df_filtrado.groupby('Período')['Nota'].mean().reset_index()

chart_media_nota = alt.Chart(df_media_nota).mark_line(point=True).encode(
    x=alt.X('Período', axis=alt.Axis(labelAngle=0)),  # Rótulos do eixo X na horizontal
    y='Nota'
).properties(
    width=600,
    height=400
)

st.altair_chart(chart_media_nota, use_container_width=True)

# Moda das Notas
st.subheader('Moda')
df_moda_nota = df_filtrado.groupby('Período')['Nota'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None).reset_index()

chart_moda_nota = alt.Chart(df_moda_nota).mark_line(point=True).encode(
    x=alt.X('Período', axis=alt.Axis(labelAngle=0)),  # Rótulos do eixo X na horizontal
    y='Nota'
).properties(
    width=600,
    height=400
)

st.altair_chart(chart_moda_nota, use_container_width=True)
