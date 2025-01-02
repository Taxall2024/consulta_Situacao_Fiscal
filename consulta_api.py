import requests
import base64
from AesEverywhere import aes256

def consultar_api(cnpj, caminho_certificado, senha_certificado, chave_criptografia, token):
    """
    Consulta a API da Infosimples para situação fiscal.
    
    Parâmetros:
        cnpj (str): CNPJ a ser consultado.
        caminho_certificado (str): Caminho do arquivo .pfx do certificado.
        senha_certificado (str): Senha do certificado.
        chave_criptografia (str): Chave para criptografia dos parâmetros.
        token (str): Token de acesso à API.

    Retorno:
        dict: Resultado da consulta à API (sucesso ou erro).
    """
    # URL da API
    url = 'https://api.infosimples.com/api/v2/consultas/ecac/situacao-fiscal'
    
    # Criptografar certificado
    try:
        certificado = base64.b64encode(open(caminho_certificado, "rb").read()).decode()
        pkcs12_cert = aes256.encrypt(certificado, chave_criptografia).decode('utf-8')
    except Exception as e:
        return {"code": 500, "message": f"Erro ao criptografar o certificado: {str(e)}"}
    
    # Criptografar senha
    try:
        pkcs12_pass = aes256.encrypt(senha_certificado, chave_criptografia).decode('utf-8')
    except Exception as e:
        return {"code": 500, "message": f"Erro ao criptografar a senha: {str(e)}"}
    
    # Parâmetros da requisição
    args = {
        "pkcs12_cert": pkcs12_cert,
        "pkcs12_pass": pkcs12_pass,
        "perfil_procurador_cnpj": cnpj,
        "token": token,
        "timeout": 300
    }

    # Realizar requisição à API
    try:
        response = requests.post(url, json=args)
        response_json = response.json()
        response.close()

        # Verificar resposta
        if response_json.get('code') == 200:
            return {"code": 200, "data": response_json['data'], "site_receipts": response_json.get('site_receipts')}
        elif response_json.get('code') in range(600, 799):
            return {
                "code": response_json['code'],
                "message": response_json.get('code_message', 'Erro desconhecido'),
                "errors": response_json.get('errors', [])
            }
        else:
            return {"code": 500, "message": "Resposta inesperada da API.", "response": response_json}

    except requests.exceptions.RequestException as e:
        return {"code": 500, "message": f"Erro na conexão com a API: {str(e)}"}
    except Exception as e:
        return {"code": 500, "message": f"Erro inesperado: {str(e)}"}