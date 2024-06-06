import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Título da aplicação
st.title("Gráfico de Distribuição Normal")

# Parâmetros da distribuição normal
mu = st.slider("Média (mu)", -10.0, 10.0, 0.0)
sigma = st.slider("Desvio Padrão (sigma)", 0.1, 5.0, 1.0)
n = st.slider("Número de pontos", 100, 10000, 1000)

# Gerar dados
data = np.random.normal(mu, sigma, n)

# Criar o gráfico
fig, ax = plt.subplots()
sns.histplot(data, kde=True, ax=ax)
ax.set(title="Distribuição Normal", xlabel="Valor", ylabel="Frequência")

# Exibir o gráfico no Streamlit
st.pyplot(fig)

fig = px.histogram(data, nbins=50, marginal="box", title="Distribuição Normal")
fig.update_layout(xaxis_title="Valor", yaxis_title="Frequência")

# Exibir o gráfico no Streamlit
st.plotly_chart(fig)
