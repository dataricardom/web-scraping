# Biblioteca para realizar requisições HTTP (GET, POST, etc.)
import requests

# Biblioteca para fazer o parser (análise estrutural) de HTML/XML
from bs4 import BeautifulSoup

# Cria uma sessão HTTP persistente
# A Session permite reutilizar conexões TCP, manter cookies entre requisições
# e preservar cabeçalhos ou estados (como autenticação ou tokens CSRF).
# É essencial em fluxos que exigem múltiplas interações com o mesmo servidor, como login seguido de navegação autenticada.
with requests.Session() as s:

    # URL da API de login do CodeChef
    login_url = 'https://www.codechef.com/api/codechef/login'

    # Primeira requisição GET para acessar a página e capturar tokens CSRF necessários para o login
    context = s.get(login_url)

    # Analisa o HTML da resposta usando BeautifulSoup
    soup = BeautifulSoup(context.content, 'html.parser')

    # Extrai o token CSRF do HTML (evita ataques de falsificação de requisição)
    csrf_token = soup.find_all('input')[3]['value']
    token_clear = csrf_token.replace('\\"', "")  # Limpa o token de possíveis caracteres escapados

    # Extrai o token de construção do formulário (form_build_id), necessário para a submissão do login
    form_build_token = soup.find_all('input')[4]['value']
    form_build_token_cleaned = form_build_token.replace('\\"', "")  # Limpa o valor

    print(token_clear)  # Exibe o CSRF Token limpo (apenas para depuração)

    # Define os dados do formulário para autenticação
    payload = {
        'name': 'email@gmail.com',       # Usuário ou email de login
        'pass': 'senha',                         # Senha da conta
        'csrfToken': token_clear,                     # Token de verificação CSRF
        'form_build_id': form_build_token_cleaned,    # Token interno do formulário
        'form_id': 'ajax_login_form'                  # ID do formulário de login usado pela aplicação
    }

    # Envia uma requisição POST com os dados do formulário para realizar o login
    response = s.post(login_url, data=payload)

    # Verifica se o login foi bem-sucedido pela resposta HTTP (200 = OK)
    if response.status_code == 200:
        print(response)