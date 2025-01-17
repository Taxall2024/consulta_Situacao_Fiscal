import streamlit as st
import pandas as pd
import ast  # Para converter strings de listas/dicionários para objetos Python

# Configuração do caminho do CSV
caminho_csv = r"G:\Drives compartilhados\Operacional\12 - CONTROLES\SITUAÇÃO FISCAL E CND\planilhas_controle\resultados_consultas_9.csv"

# Função para transformar o JSON do campo "data" em um DataFrame
def transformar_json_em_tabela(data_json):
    registros = []
    pendencias_rf_json = []  # Lista para armazenar os dados de pendências da Receita Federal
    pendencias_pgfn_json = []  # Lista para armazenar os dados de pendências da Procuradoria Geral

    for registro in data_json:
        try:
            certidao = registro.get('certidao_emitida', {}).get('obs', 'N/A')
            endereco = registro.get('dados_cadastrais_pj_matriz', {}).get('endereco', 'N/A')
            municipio = registro.get('dados_cadastrais_pj_matriz', {}).get('municipio', 'N/A')
            uf = registro.get('dados_cadastrais_pj_matriz', {}).get('uf', 'N/A')
            pendencias_rf = registro.get('pendencias_receita_federal', [])
            pendencias_pgfn = registro.get('pendencias_procuradoria_geral', [])
            link_certidao = registro.get('site_receipt', 'N/A')
            data_consulta = registro.get('data_hora_consulta', 'N/A')

            try:
                data_consulta = pd.to_datetime(data_consulta, errors='coerce').strftime("%Y-%m-%d")
            except Exception:
                data_consulta = None


            # Adicionar `data_consulta` aos JSONs para pendências
            for item in pendencias_rf:
                item['data_consulta'] = data_consulta
            for item in pendencias_pgfn:
                item['data_consulta'] = data_consulta

            # Armazenar os JSONs completos para posterior processamento
            pendencias_rf_json.extend(pendencias_rf)
            pendencias_pgfn_json.extend(pendencias_pgfn)

            # Adicionar registro para a tabela principal
            registros.append({
                "Certidão": certidao,
                "Endereço": endereco,
                "Município": municipio,
                "UF": uf,
                "Pendências Receita Federal": ", ".join([p.get('tipo', 'N/A') for p in pendencias_rf]),
                "Pendências PGFN": ", ".join([p.get('tipo', 'N/A') for p in pendencias_pgfn]),
                "Link Certidão": link_certidao,
                "Data Consulta": data_consulta
            })
        except Exception as e:
            st.error(f"Erro ao processar registro: {e}")

    return pd.DataFrame(registros), pendencias_rf_json, pendencias_pgfn_json

# Função para criar DataFrames a partir de listas de pendências
def criar_tabela_pendencias(data, coluna_nome):
    if not data:
        return None, None  # Retornar None se os dados estiverem vazios

    # Criar DataFrame com apenas as colunas "tipo" e "data_consulta"
    df = pd.DataFrame(data)
    if 'tipo' in df.columns and 'data_consulta' in df.columns:
        df = df[['tipo', 'data_consulta']]
    

    sub_tabelas = {}

    # Verificar se há débitos em algum registro
    debitos_registros = [
        {"debitos": item.get('debitos', []), "tipo": item.get('tipo', 'N/A')} 
        for item in data if 'debitos' in item and item['debitos']
    ]
    
    if debitos_registros:
        debitos = pd.json_normalize(
            debitos_registros, 
            'debitos', 
            ['tipo'], 
            errors='ignore'
        )

        debitos = debitos.loc[:, ~debitos.columns.str.startswith(('normalizado_', 'normalziado_'))]
        sub_tabelas['debitos'] = debitos
    
    parcelamento_registros = [
        item for item in data if 'parcelamento' in item and item['parcelamento']
    ]
    if parcelamento_registros:
        parcelamento_df = pd.DataFrame(parcelamento_registros)
        # Remover a coluna data_consulta apenas para a subtabela parcelamento
        if 'data_consulta' in parcelamento_df.columns:
            parcelamento_df = parcelamento_df.drop(columns=['data_consulta'])
        #parcelamento_df = parcelamento_df.loc[:, ~parcelamento_df.columns.str.startswith(('normalizado_', 'normalziado_'))]
        sub_tabelas['parcelamento'] = parcelamento_df

    return df, sub_tabelas

# Início da aplicação Streamlit
st.title("Resultados das Consultas Fiscais")

# Ler o CSV
try:
    df = pd.read_csv(caminho_csv, sep=';')
    df['data'] = df['data'].apply(lambda x: ast.literal_eval(x))  # Converter string para lista de dicionários

    # Garantir que a coluna `data_consulta` exista
    if 'data_consulta' not in df.columns:
        df['data_consulta'] = df['data'].apply(
            lambda data: data[0].get('data_hora_consulta', 'N/A') if isinstance(data, list) and data else 'N/A'
        )

    # Converter `data_consulta` para o formato de data e formatar como yyyy-mm-dd
    #df['data_consulta'] = pd.to_datetime(df['data_consulta'], errors='coerce').strftime("%Y-%m-%d")
except Exception as e:
    st.error(f"Erro ao carregar o CSV: {e}")
    st.stop()

# Filtro por razão social
razao_social = st.sidebar.selectbox("Selecione a Razão Social:", options=df["RAZÃO SOCIAL"].unique())
dados_filtrados = df[df["RAZÃO SOCIAL"] == razao_social]

# Filtro por data de consulta
# datas_consulta = sorted(df['data_consulta'].dropna().unique())
# data_selecionada = st.sidebar.selectbox("Selecione a Data de Consulta:", options=datas_consulta)
# df = df[df['data_consulta'] == data_selecionada]

if not dados_filtrados.empty:
    # Converter campo "data" em tabela principal e obter os JSONs das pendências
    tabela_dados, pendencias_rf_json, pendencias_pgfn_json = transformar_json_em_tabela(dados_filtrados.iloc[0]['data'])

    # Verificar se ambos os JSONs estão vazios
    if not pendencias_rf_json and not pendencias_pgfn_json:
        st.write("Tabela Geral:")
        st.dataframe(tabela_dados)
    else:
        # Criar DataFrames para as pendências
        pendencias_pgfn, sub_tabelas_pgfn = criar_tabela_pendencias(pendencias_pgfn_json, "Pendências PGFN")
        pendencias_rf, sub_tabelas_rf = criar_tabela_pendencias(pendencias_rf_json, "Pendências Receita Federal")

        # Criar abas para exibir os dados
        tab1, tab2, tab3 = st.tabs(["Tabela Geral", "Pendências PGFN", "Pendências Receita Federal"])

        with tab1:
            st.write("Dados Consulta Fiscal:")
            st.dataframe(tabela_dados)

        with tab2:
            if pendencias_pgfn is not None:
                st.write("Pendências da Procuradoria Geral:")
                st.dataframe(pendencias_pgfn)
                if sub_tabelas_pgfn:
                    if 'debitos' in sub_tabelas_pgfn:
                        st.write(f"Detalhes {', '.join(sub_tabelas_pgfn['debitos']['tipo'].unique())}:")
                        st.dataframe(sub_tabelas_pgfn['debitos'])
                    if 'parcelamento' in sub_tabelas_pgfn:
                        st.write("Detalhe dos Parcelamentos:")
                        st.dataframe(sub_tabelas_pgfn['parcelamento'])

        with tab3:
            if pendencias_rf is not None:
                st.write("Pendências da Receita Federal:")
                st.dataframe(pendencias_rf)
                if sub_tabelas_rf:
                    if 'debitos' in sub_tabelas_rf:
                        st.write(f"Detalhes {', '.join(sub_tabelas_rf['debitos']['tipo'].unique())}:")
                        st.dataframe(sub_tabelas_rf['debitos'])
                    if 'parcelamento' in sub_tabelas_rf:
                        st.write("Detalhe dos Parcelamentos:")
                        st.dataframe(sub_tabelas_rf['parcelamento'])
else:
    st.warning("Nenhum dado encontrado para a razão social selecionada.")
