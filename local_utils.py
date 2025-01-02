import os

def criar_pasta_local(base_path, nome_pasta):
    """
    Cria uma pasta local dentro do diretório especificado.

    Parâmetros:
        base_path (str): Caminho base onde a pasta será criada.
        nome_pasta (str): Nome da pasta a ser criada.

    Retorno:
        str: Caminho completo da pasta criada.
    """
    caminho_pasta = os.path.join(base_path, nome_pasta)
    try:
        os.makedirs(caminho_pasta, exist_ok=True)
        print(f"Pasta criada ou já existente: {caminho_pasta}")
    except Exception as e:
        print(f"Erro ao criar pasta local: {e}")
    return caminho_pasta