import pandas as pd

def transformar_resultado_api_em_dataframe(data):
    """
    Converte os dados retornados pela API em um DataFrame sem manipulação específica.

    Parâmetros:
        data (list[dict]): Lista de dicionários com os resultados da API.

    Retorna:
        pd.DataFrame: DataFrame gerado diretamente a partir dos dados.
    """
    try:
        # Converte diretamente a lista de dicionários para DataFrame
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Erro ao transformar os dados em DataFrame: {str(e)}")
        return pd.DataFrame()
