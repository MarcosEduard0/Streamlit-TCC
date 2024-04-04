import streamlit as st
import pandas as pd
import plotly.graph_objs as go

st.title('Dashboard de Histórico de CR')

# Carregar dados
try:
    data = pd.read_csv('craPorPeriodo.csv', sep=';')
    st.write('DataFrame carregado com sucesso:')
    st.write(data.head())  # Mostra as primeiras linhas do DataFrame para verificação
except FileNotFoundError:
    st.error('Arquivo CSV não encontrado. Verifique o caminho do arquivo.')

# Criar histograma do CR ao longo do tempo
st.subheader('Histórico de CR')
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

# Criar histograma da média CR ao longo do tempo, de todos os alunos
st.subheader('Média de CR')
# Calcular a média dos CRs para cada período
mean_cr_per_period = data.groupby('periodo')['cr'].mean()

# Selecionar os períodos de interesse usando um widget de seleção múltipla
selected_periods = st.multiselect('Selecione os períodos:', mean_cr_per_period.index)

if st.button('Atualizar Média de CR'):
    # Filtrar os dados para os períodos selecionados e excluir os CRs vazios
    filtered_mean_cr = mean_cr_per_period.loc[selected_periods]
    filtered_mean_cr = filtered_mean_cr.dropna()

    # Plotar as médias dos CRs para os períodos selecionados
    fig_mean_cr = go.Figure()
    fig_mean_cr.add_trace(go.Scatter(x=filtered_mean_cr.index, y=filtered_mean_cr.values, mode='lines+markers'))
    fig_mean_cr.update_layout(xaxis_title='Período', yaxis_title='Média do CR', title='Média do CR ao Longo do Tempo')
    st.plotly_chart(fig_mean_cr)

    # Exibir os dados para os períodos selecionados
    st.write('Média dos CRs para os períodos selecionados (excluindo CRs vazios):')
    st.write(filtered_mean_cr)
