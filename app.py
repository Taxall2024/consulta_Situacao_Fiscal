import streamlit as st
import pandas as pd
import ast  # Para converter strings de listas/dicionários para objetos Python

# Configuração do caminho do CSV
caminho_csv = fr"G:\Drives compartilhados\Operacional\12 - CONTROLES\SITUAÇÃO FISCAL E CND\planilhas_controle\resultados_consultas_9.csv"
# Função para transformar o JSON do campo "data" em um DataFrame
def transformar_json_em_tabela(data_json):
    registros = []
    for registro in data_json:
        try:
            certidao = registro.get('certidao_emitida', {}).get('obs', 'N/A')
            endereco = registro.get('dados_cadastrais_pj_matriz', {}).get('endereco', 'N/A')
            municipio = registro.get('dados_cadastrais_pj_matriz', {}).get('municipio', 'N/A')
            uf = registro.get('dados_cadastrais_pj_matriz', {}).get('uf', 'N/A')
            pendencias_rf = ", ".join([p.get('tipo', 'N/A') for p in registro.get('pendencias_receita_federal', [])])
            pendencias_pgfn = ", ".join([p.get('tipo', 'N/A') for p in registro.get('pendencias_procuradoria_geral', [])])
            link_certidao = registro.get('site_receipt', 'N/A')
            data_consulta = registro.get('data_hora_consulta', 'N/A')

            registros.append({
                "Certidão": certidao,
                "Endereço": endereco,
                "Município": municipio,
                "UF": uf,
                "Pendências Receita Federal": pendencias_rf,
                "Pendências PGFN": pendencias_pgfn,
                "Link Certidão": link_certidao,
                "Data Consulta": data_consulta,
            })
        except Exception as e:
            st.error(f"Erro ao processar registro: {e}")
    return pd.DataFrame(registros)

# Início da aplicação Streamlit
st.title("Visualização de Resultados das Consultas Fiscais")

# Ler o CSV
try:
    df = pd.read_csv(caminho_csv, sep=';')
    df['data'] = df['data'].apply(lambda x: ast.literal_eval(x))  # Converter string para lista de dicionários
except Exception as e:
    st.error(f"Erro ao carregar o CSV: {e}")
    st.stop()

# Filtro por razão social
razao_social = st.selectbox("Selecione a Razão Social:", options=df["RAZÃO SOCIAL"].unique())

# Filtrar os dados pelo CNPJ selecionado
dados_filtrados = df[df["RAZÃO SOCIAL"] == razao_social]

if not dados_filtrados.empty:
    # Converter campo "data" em tabela
    tabela_dados = transformar_json_em_tabela(dados_filtrados.iloc[0]['data'])
    st.write("Dados da Consulta Fiscal:")
    st.dataframe(tabela_dados)
else:
    st.warning("Nenhum dado encontrado para a razão social selecionada.")