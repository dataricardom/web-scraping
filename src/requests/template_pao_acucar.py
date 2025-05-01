# Biblioteca padrão para expressões regulares (usada para extrair número da página da URL)
import re

# Biblioteca para fazer requisições HTTP
import requests

# Adaptador da biblioteca 'requests' para configurar tentativas automáticas de requisição
from requests.adapters import HTTPAdapter

# Utilitário para definir estratégias de retry com a biblioteca 'urllib3'
from urllib3.util import Retry

# Biblioteca para manipulação e análise de dados em formato tabular (não usada no código, mas útil se quiser gerar DataFrame)
import pandas as pd


# Classe para fazer scraping de produtos do site Pão de Açúcar via API Linx Impulse
class PaoDeAcucarScraper:
    def __init__(self):
        # Configura a sessão HTTP com retry automático
        self.http = self._configure_session()

        # Define a origem do site usada nas requisições
        self.origin = 'https://www.paodeacucar.com'

        # Lista para armazenar os produtos extraídos
        self.products = []

        # Chave da API usada na URL de requisição
        self.api_key = 'paodeacucar'

        # Armazena a resposta JSON da API
        self.content = None

    # Método principal para iniciar a busca de produtos
    def start(self, keyword: str, page: int = None, results_per_page: int = None):
        # Define a página inicial; se não for passada, assume como 1
        self.page = page or 1

        # Define quantos resultados por página; se não for passado, assume 12
        self.results_per_page = results_per_page or 12

        # Faz a primeira busca com a palavra-chave
        self.search_products(keyword)

        # Recupera o número total de páginas baseado na resposta da API
        total_pages = self.get_total_pages()

        # Percorre as páginas a partir da 2 até a última
        for i in range(2, total_pages):
            # Atualiza o número da página atual
            self.page = i

            # Coleta os produtos da página atual e adiciona à lista
            self.products = [*self.products, *self.get_product_data()]

            # Realiza nova busca com a palavra-chave para a próxima página
            self.search_products(keyword)

        # Retorna todos os produtos coletados
        return self.products

    # Configura a sessão HTTP com política de retry em caso de falhas
    def _configure_session(self):
        retry_strategy = Retry(
            total=3,  # número máximo de tentativas
            status_forcelist=[403, 404, 429, 500, 502, 503, 504]  # erros em que deve tentar novamente
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()  # cria uma nova sessão
        session.mount("https://", adapter)  # aplica retry para HTTPS
        session.mount("http://", adapter)   # aplica retry para HTTP
        return session

    # Gera os cabeçalhos HTTP usados na requisição à API
    def get_headers(self):
        return {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': self.origin,
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    # Realiza a busca de produtos na API com base na palavra-chave e na página atual
    def search_products(self, keyword):
        # Monta a URL da API com os parâmetros necessários
        api_url = (
            f'https://api.linximpulse.com/engage/search/v3/search?apikey={self.api_key}'
            f'&origin={self.origin}&page={self.page}&resultsPerPage={self.results_per_page}&terms={keyword}'
            f'&allowRedirect=true&salesChannel=461&salesChannel=catalogmkp&sortBy=relevance'
        )

        headers = self.get_headers()

        try:
            # Faz a requisição GET para a API
            response = self.http.get(api_url, headers=headers)
            response.raise_for_status()

            # Se a resposta for bem-sucedida (status 200), armazena o JSON na variável content
            if response.status_code == 200:
                self.content = response.json()
            else:
                raise(response.status_code)
        except requests.exceptions.RequestException as e:
            # Em caso de erro na requisição, exibe mensagem de erro
            raise(f"Erro ao fazer requisição: {e}") 

    # Extrai os dados dos produtos do JSON retornado pela API
    def get_product_data(self):
        if self.content:
            products = self.content["products"]
            return products
        else:
            print(f"Erro na resposta: {self.content}")
            return []

    # Obtém o número total de páginas a partir da URL de paginação retornada pela API
    def get_total_pages(self):
        last_page = 1

        # Acessa o objeto de paginação
        pagination = self.content["pagination"]
        last_page_url = pagination["last"]

        # Usa regex para extrair o número da última página da URL
        pattern = r'page=(\d+)'
        match = re.search(pattern, last_page_url)
        if match:
            page_value = match.group(1)
            print(f"O valor da página é: {page_value}")
            last_page = page_value

        # Converte para inteiro e retorna
        return int(last_page)


# Uso da classe
keyword = 'cerveja'  # palavra-chave a ser buscada
scraper = PaoDeAcucarScraper()  # cria uma instância do scraper
data = scraper.start(keyword)  # inicia o processo de scraping

# Exibe os produtos coletados
if data:
    print(data)
