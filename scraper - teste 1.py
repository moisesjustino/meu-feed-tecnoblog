# -*- coding: utf-8 -*-

# Adicione 'requests' aos seus imports no topo do arquivo
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
import datetime

# --- CONFIGURAÇÕES E DADOS DE EXEMPLO (A SEREM SUBSTITUÍDOS NA ETAPA 2) ---
# Arquivo HTML que vamos analisar (você vai criá-lo na próxima etapa)
# NOME_ARQUIVO_HTML = 'pagina_alvo.html'
# Nome do arquivo RSS que será gerado
NOME_ARQUIVO_RSS = 'feed_tecnoblog.xml'

# ADICIONE ESTA LINHA:
URL_ALVO = 'https://tecnoblog.net/' # URL do site que vamos raspar

# URL base do site alvo (importante para montar links completos)
URL_BASE = 'https://tecnoblog.net'
# Título e descrição do seu feed
FEED_TITULO = 'Tecnoblog - Feed RSS Não Oficial'
FEED_DESCRICAO = 'As últimas notícias de tecnologia do Tecnoblog.'

# Seletores CSS (ATUALMENTE VAZIOS - SERÃO PREENCHIDOS NA ETAPA 2)
SELETOR_CONTAINER_ARTIGO = 'article'
SELETOR_TITULO = 'h2' # O título é o h2 dentro do artigo
SELETOR_LINK = 'a' # O link é a tag <a> dentro do artigo
SELETOR_RESUMO = '' # Ainda não encontramos um resumo, então deixamos vazio
# --- FIM DAS CONFIGURAÇÕES ---


def gerar_feed_online():
    """Baixa o HTML de uma URL e gera um feed RSS."""
    
    print(f"Iniciando scraper online para: {URL_ALVO}")
    
    # Validação inicial: verifica se os seletores foram preenchidos
    if not all([SELETOR_CONTAINER_ARTIGO, SELETOR_TITULO, SELETOR_LINK]):
        print("\nERRO: Seletores essenciais não definidos.")
        return

    # 1. Tenta ler o arquivo HTML local
    try:
        # Headers para simular um navegador e evitar bloqueios simples
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL_ALVO, headers=headers, timeout=10)
        response.raise_for_status()  # Lança um erro se a requisição falhar (ex: 404, 500)

        # Analisa o conteúdo baixado com o BeautifulSoup
        soup = BeautifulSoup(response.content, 'lxml')

    except requests.exceptions.RequestException as e:
        print(f"\nERRO: Falha ao baixar a página. Motivo: {e}")
        return
        

    # 2. Configura o objeto do Feed
    fg = FeedGenerator()
    fg.title(FEED_TITULO)
    fg.link(href=URL_BASE, rel='alternate')
    fg.description(FEED_DESCRICAO)
    fg.language('pt-BR')
    fg.lastBuildDate(datetime.datetime.now(datetime.timezone.utc))

    # 3. Extrai os dados usando os seletores
    artigos_encontrados = soup.select(SELETOR_CONTAINER_ARTIGO)
    print(f"Encontrados {len(artigos_encontrados)} itens usando o seletor de contêiner.")

    for item in artigos_encontrados:
        try:
            titulo_tag = item.select_one(SELETOR_TITULO)
            link_tag = item.select_one(SELETOR_LINK)
            
            # Pula o item se não encontrar título ou link
            if not (titulo_tag and link_tag):
                continue

            titulo = titulo_tag.get_text(strip=True)
            link_relativo = link_tag.get('href', '')
            link_absoluto = urljoin(URL_BASE, link_relativo)
            
            # O resumo é opcional
            resumo = ''
            if SELETOR_RESUMO:
                resumo_tag = item.select_one(SELETOR_RESUMO)
                if resumo_tag:
                    resumo = resumo_tag.get_text(strip=True)

            # Adiciona a entrada (entry) ao feed
            fe = fg.add_entry()
            fe.id(link_absoluto)
            fe.title(titulo)
            fe.link(href=link_absoluto)
            fe.description(resumo)
            
        except Exception as e:
            print(f"Ocorreu um erro ao processar um item: {e}")
            continue

    # 4. Gera o arquivo XML
    if len(artigos_encontrados) > 0:
        fg.rss_file(NOME_ARQUIVO_RSS, pretty=True)
        print(f"\nSUCESSO! Feed RSS foi gerado e salvo como '{NOME_ARQUIVO_RSS}'.")
    else:
        print("\nAVISO: Nenhum item foi encontrado. O arquivo RSS não foi gerado.")

# Atualize a chamada no final do script
if __name__ == "__main__":
    gerar_feed_online() # Chamando a nova função