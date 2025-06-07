# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin
import datetime
import time

# --- CONFIGURAÇÕES ---
URL_ALVO = 'https://tecnoblog.net/'
URL_BASE = 'https://tecnoblog.net'
NOME_ARQUIVO_RSS = 'feed_tecnoblog.xml'

FEED_TITULO = 'Tecnoblog - Feed RSS (Completo)'
FEED_DESCRICAO = 'Últimas notícias do Tecnoblog, com imagens, resumos e datas.'

# --- SELETORES FINAIS ---
SELETOR_CONTAINER_ARTIGO = 'article'
SELETOR_TITULO = 'h2'
SELETOR_LINK = 'a'
SELETOR_IMAGEM = 'img'
SELETOR_RESUMO_INTERNO = 'p.olho'
# SELETOR FINAL PARA A DATA
SELETOR_DATA_INTERNA = 'div.time time' 
# --- FIM DAS CONFIGURAÇÕES ---

def gerar_feed_completo():
    print(f"Iniciando scraper completo para: {URL_ALVO}")
    
    headers = { 'User-Agent': 'Mozilla/5.0 ...' }

    try:
        print("Baixando a página principal...")
        response_principal = requests.get(URL_ALVO, headers=headers, timeout=15)
        response_principal.raise_for_status()
        soup_principal = BeautifulSoup(response_principal.content, 'lxml')
    except requests.exceptions.RequestException as e:
        print(f"\nERRO: Falha ao baixar a página principal. Motivo: {e}")
        return

    fg = FeedGenerator()
    fg.title(FEED_TITULO)
    fg.link(href=URL_BASE, rel='alternate')
    fg.description(FEED_DESCRICAO)
    fg.language('pt-BR')

    artigos_encontrados = soup_principal.select(SELETOR_CONTAINER_ARTIGO)
    print(f"Encontrados {len(artigos_encontrados)} artigos. Processando cada um...")

    for item in artigos_encontrados:
        try:
            # ... (código para título e link)
            titulo_tag = item.select_one(SELETOR_TITULO)
            link_tag = item.select_one(SELETOR_LINK)
            if not (titulo_tag and link_tag and link_tag.get('href')):
                continue
            titulo = titulo_tag.get_text(strip=True)
            link_absoluto = urljoin(URL_BASE, link_tag.get('href', ''))
            print(f"  - Processando: {titulo}")

            # ... (código para imagem)
            imagem_url = None
            imagem_tag = item.select_one(SELETOR_IMAGEM)
            if imagem_tag:
                imagem_url = imagem_tag.get('data-src') or imagem_tag.get('src')
            
            # --- LÓGICA DE BUSCA INTERNA ---
            descricao = "Sem descrição breve."
            data_publicacao = None # Inicia a variável como nula
            try:
                time.sleep(0.5)
                response_artigo = requests.get(link_absoluto, headers=headers, timeout=10)
                if response_artigo.status_code == 200:
                    soup_artigo = BeautifulSoup(response_artigo.content, 'lxml')
                    
                    # Busca a descrição
                    resumo_tag = soup_artigo.select_one(SELETOR_RESUMO_INTERNO)
                    if resumo_tag:
                        descricao = resumo_tag.get_text(strip=True)

                    # Busca a data
                    data_tag = soup_artigo.select_one(SELETOR_DATA_INTERNA)
                    if data_tag and data_tag.get('datetime'):
                        data_string_iso = data_tag.get('datetime')
                        # Converte a string para um objeto datetime
                        data_publicacao = datetime.datetime.fromisoformat(data_string_iso)

            except requests.exceptions.RequestException:
                print(f"    - Aviso: Não foi possível buscar detalhes para '{titulo}'")

            # --- Adiciona a entrada completa ao feed ---
            fe = fg.add_entry()
            fe.id(link_absoluto)
            fe.title(titulo)
            fe.link(href=link_absoluto)
            fe.description(descricao)
            
            # Adiciona a data de publicação, se encontrada
            if data_publicacao:
                fe.pubDate(data_publicacao)
            
            if imagem_url:
                fe.enclosure(url=imagem_url, length='0', type='image/jpeg')

        except Exception as e:
            print(f"Ocorreu um erro ao processar um item: {e}")
            continue

    fg.rss_file(NOME_ARQUIVO_RSS, pretty=True)
    print(f"\nSUCESSO! Feed completo foi gerado e salvo como '{NOME_ARQUIVO_RSS}'.")

if __name__ == "__main__":
    gerar_feed_completo()