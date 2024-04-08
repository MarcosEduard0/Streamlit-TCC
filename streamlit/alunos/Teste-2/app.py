import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from matplotlib import pyplot as plt

st.title('Dashboard IC-UFRJ')

# Lista de nomes dos arquivos a serem carregados
file_names = [
    'd_aluno',
    'd_curso',
    'd_disciplina',
    'd_periodo',
    'f_desempenho_academico',
    'f_matricula_aluno'
]

# Função para carregar os dados de um arquivo CSV
def load_data(file_name):
    try:
        data = pd.read_csv(f'data/{file_name}.csv', sep=',')
        st.write(f'DataFrame {file_name} carregado com sucesso:')
        st.write(data.head())  # Mostra as primeiras linhas do DataFrame para verificação
    except FileNotFoundError:
        st.error(f'Arquivo {file_name}.csv não encontrado. Verifique o caminho do arquivo.')

# Função para mostrar a aba de carregamento de arquivos CSV
def load_data_tab():
    st.write("Carregar Arquivos:")
    for file_name in file_names:
        load_data(file_name)

# Função para mostrar a aba do Histórico de CR
def show_cr_history_tab():
    st.write("Histórico de CR")
    # Campo para digitar a matrícula
    matricula_input = st.number_input('Digite a matrícula desejada (exemplo: 12):', format='%d', step=1)
    # Botão para acionar a atualização dos dados
    if st.button('Atualizar Histórico de CR'):
        # Verifica se a matrícula é válida
        if matricula_input not in data['matriculaDRE'].unique():
            st.warning('Matrícula não encontrada. Por favor, verifique a matrícula inserida.')
        else:
            # Filtrar dados para a matrícula selecionada
            data_filtered = data[data['matriculaDRE'] == matricula_input]
            
            # Ordena os dados pelo período
            data_filtered.sort_values(by='periodo', inplace=True)

            # Cria o gráfico de linha
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=data_filtered['periodo'], y=data_filtered['cr'], mode='lines+markers'))
            fig_line.update_layout(xaxis_title='Período', yaxis_title='CR', title='Histórico de CR ao Longo do Tempo')
            st.plotly_chart(fig_line)  # Passa o gráfico para st.plotly_chart()

            # Exibir dataframe filtrado
            st.write('Dados para Matrícula Selecionada:', data_filtered)





# Função para mostrar a aba da Média de CR
def show_cr_mean_tab():
    # Carregar os arquivos CSV em DataFrames
    aluno_data = pd.read_csv('data/d_aluno.csv')
    desempenho_data = pd.read_csv('data/f_desempenho_academico.csv')
    periodo_data = pd.read_csv('data/d_periodo.csv')

    # Mesclar os dados dos arquivos para calcular a média do CR ao longo do tempo
    merged_data = desempenho_data.merge(aluno_data, on='sk_d_aluno').merge(periodo_data, on='sk_d_periodo')

    # Filtrar o ano e semestre únicos do arquivo d_periodo.csv para a seleção do usuário
    unique_years_semesters = list(zip(periodo_data['ano'], periodo_data['semestre']))
    selected_periods = st.multiselect('Selecione os períodos:', unique_years_semesters)

    # Filtrar os dados pelo ano e semestre selecionados pelo usuário
    filtered_data = merged_data[(merged_data['ano'].isin([ano for ano, _ in selected_periods])) & 
                                (merged_data['semestre'].isin([semestre for _, semestre in selected_periods]))]

    # Calcular a média dos CRs para cada ano e período
    mean_cr_per_period = filtered_data.groupby(['ano', 'semestre'])['cr_periodo'].mean().reset_index()

    # Plotar as médias dos CRs para os anos e períodos selecionados
    fig_mean_cr = go.Figure()
    for periodo in selected_periods:
        ano, semestre = periodo
        mean_cr = mean_cr_per_period[(mean_cr_per_period['ano'] == ano) & (mean_cr_per_period['semestre'] == semestre)]['cr_periodo'].values[0]
        fig_mean_cr.add_trace(go.Scatter(x=[f'{ano} - Semestre {semestre}'], y=[mean_cr], mode='lines+markers', name=f'{ano} - Semestre {semestre}'))

    # Calcular a linha suave que passe por todos os pontos do gráfico
    x = [f'{ano} - Semestre {semestre}' for ano, semestre in selected_periods]
    y = [mean_cr_per_period[(mean_cr_per_period['ano'] == ano) & (mean_cr_per_period['semestre'] == semestre)]['cr_periodo'].values[0] for ano, semestre in selected_periods]

    fig_mean_cr.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Linha Suave', line=dict(color='blue', width=2, smoothing=0.3)))
    fig_mean_cr.update_layout(xaxis_title='Período', yaxis_title='Média do CR', title='Média do CR ao Longo do Tempo')
    st.plotly_chart(fig_mean_cr)
    

# Menu lateral para selecionar a aba
selected_tab = st.sidebar.radio("Selecione uma aba:", [
    "Carregar Arquivos", "Histórico de CR", "Média de CR"])

# Mostrar a aba selecionada
if selected_tab == "Carregar Arquivos":
    load_data_tab()
elif selected_tab == "Histórico de CR":
    show_cr_history_tab()
elif selected_tab == "Média de CR":
    show_cr_mean_tab()
