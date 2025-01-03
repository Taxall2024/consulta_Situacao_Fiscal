import pandas as pd
import requests
import os
import time

from consulta_api import consultar_api
from data_transform import transformar_resultado_api_em_dataframe
from local_utils import criar_pasta_local  # Importação modularizada
from datetime import datetime
from decouple import config  # Para carregar variáveis do arquivo .env

start = time.time()


senha_certificado = config("SENHA_CERTIFICADO")
chave_criptografia = config("CHAVE_CRIPTOGRAFIA")
token = config("TOKEN")

caminho_certificado = r"C:\Users\hailleen.gonzalez\Documents\Projeto Situação Fiscal\1_data\input\TAX ALL SSA.pfx"
caminho_csv = r"G:\Drives compartilhados\Operacional\12 - CONTROLES\SITUAÇÃO FISCAL E CND\planilhas_controle\resultados_consultas.csv"
pasta_pdfs_local = r"G:\Drives compartilhados\Operacional\12 - CONTROLES\SITUAÇÃO FISCAL E CND"

# Criar a pasta local de PDFs, se não existir
os.makedirs(pasta_pdfs_local, exist_ok=True)

arquivo_excel = r"G:\Drives compartilhados\Operacional\33 - TRANSFORMAÇÃO ORGANIZACIONAL\00_old\20240802_Compensação\02_Em elaboração\20241209_Controle_Empresas_Certificado.xlsx"

try:
    df_cnpjs = pd.read_excel(arquivo_excel, sheet_name=0)
    print("Dados carregados com sucesso!")
    print(df_cnpjs.head())
except Exception as e:
    print(f"Erro ao carregar dados do Google Sheets: {str(e)}")
    exit()

# Etapa 2: Contar CNPJs únicos
df_cnpjs = df_cnpjs[df_cnpjs['CND'] == 'SIM'][39:40]
cnpjs_unicos = df_cnpjs["CNPJ"].nunique()

print(f"Número de CNPJs únicos: {cnpjs_unicos}")

# Etapa 3: Iterar pelos CNPJs e realizar consultas
resultados = []

for _, cliente in df_cnpjs.iterrows():
    cnpj = cliente["CNPJ"]
    razao_social = cliente["EMPRESA"]

    print(f"Consultando CNPJ: {cnpj} - {razao_social}")
    resultado = consultar_api(cnpj, caminho_certificado, senha_certificado, chave_criptografia, token)

    # Adicionar razão social aos resultados
    resultado["CNPJ"] = cnpj
    resultado["RAZÃO SOCIAL"] = razao_social

    resultados.append(resultado)

# Etapa 4: Transformar os dados e salvar como CSV
try:
    df_transformado = transformar_resultado_api_em_dataframe(resultados)
    df_transformado.to_csv(caminho_csv, index=False, sep=';')
    print("Dados transformados e salvos no CSV com separador ';'.")
except Exception as e:
    print(f"Erro ao transformar ou salvar os dados: {str(e)}")

# Etapa 5: Filtrar retornos positivos e processar PDFs
resultados_positivos = [res for res in resultados if res.get("code") == 200]

for resultado in resultados_positivos:
    cnpj = resultado["CNPJ"]
    razao_social = resultado["RAZÃO SOCIAL"]
    data_consulta = datetime.now().strftime("%Y-%m-%d")
    site_receipts = resultado.get("site_receipts", [])

    # Garantir que site_receipts é uma lista e contém URLs válidos
    if not isinstance(site_receipts, list) or not site_receipts:
        print(f"Nenhum PDF encontrado ou formato inválido para {razao_social}")
        continue

    # Baixar e salvar o primeiro PDF localmente
    pdf_url = site_receipts[0]  # Considerando que o primeiro link seja o correto
    nome_pdf = f"{razao_social.replace(' ', '_')}_situacao-fiscal_{data_consulta}.pdf"
    caminho_cliente_pasta = criar_pasta_local(pasta_pdfs_local, razao_social.replace(' ', '_'))
    caminho_pdf_local = os.path.join(caminho_cliente_pasta, nome_pdf)

    try:
        # Baixar o PDF
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(caminho_pdf_local, "wb") as pdf_file:
            pdf_file.write(response.content)
        print(f"PDF salvo com sucesso: {nome_pdf}")
    except Exception as e:
        print(f"Erro ao salvar PDF para {razao_social}: {str(e)}")

end = time.time()
tempo = end - start
print(f"Tempo de execução: {tempo:.2f} segundos")