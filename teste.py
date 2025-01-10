import streamlit as st
import pandas as pd

# Dados de exemplo
data1 = {
    "Nome": ["Alice", "Bob", "Charlie"],
    "Idade": [25, 30, 35],
    "Cidade": ["São Paulo", "Rio de Janeiro", "Belo Horizonte"],
}

data2 = {
    "Produto": ["Notebook", "Smartphone", "Tablet"],
    "Preço": [4500, 2000, 1500],
    "Quantidade": [10, 20, 15],
}

# Criar DataFrames
df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Título do aplicativo
st.title("Exemplo de Abas com DataFrames")

# Criando abas
tab1, tab2 = st.tabs(["Tabela de Pessoas", "Tabela de Produtos"])

with tab1:
    st.header("Tabela de Pessoas")
    st.dataframe(df1)  # Mostra o DataFrame de pessoas

with tab2:
    st.header("Tabela de Produtos")
    st.dataframe(df2)  # Mostra o DataFrame de produtos
