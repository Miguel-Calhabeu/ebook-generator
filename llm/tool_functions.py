import os
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from openai import OpenAI
from trafilatura import extract

SERP_API_KEY = "081ce010453aa85135219ca5e575bc082552f04348f6e775261135d54d4d56e2"

def web_fetch(query: str, n_sources: int = 3, max_content_length: int = 5000) -> dict:
    """
    Versão corrigida usando configuração via parâmetros ou DEFAULT_CONFIG.
    """
    try:
        # 1. Busca inicial
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": query,
            "num": n_sources,
            "api_key": os.getenv("SERP_API_KEY")
        }

        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        sources = data.get("organic_results", [])[:n_sources]

        # 2. Configuração via parâmetros diretos (sem max_tree_size)
        processed_contents = []

        for source in sources:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                page_response = requests.get(
                    source["link"],
                    timeout=30,
                    headers=headers
                )

                # 3. Extração com parâmetros válidos apenas
                content = extract(
                    page_response.text,
                    favor_precision=True,
                    include_tables=True,
                    include_formatting=False,
                    include_comments=False,
                    include_images=False,
                    no_fallback=True,  # Evita extração de baixa qualidade
                )

                # 4. Validação e processamento
                if content and len(content.strip()) > 100:
                    cleaned_content = clean_content(content, max_content_length)

                    relevance_score = calculate_relevance(
                        cleaned_content,
                        query
                    )

                    processed_contents.append({
                        "title": source.get("title"),
                        "url": source.get("link"),
                        "content": cleaned_content,
                        "score": relevance_score,
                        "length": len(cleaned_content.split())
                    })

            except Exception as e:
                print(f"Erro ao processar {source.get('link')}: {e}")
                continue

        top_contents = select_best_contents(processed_contents, max_total_tokens=10000)
        return summarize_contents(top_contents, query)

    except Exception as e:
        return {"summary": None, "error": str(e)}

def clean_content(content: str, max_length: int) -> str:
    """Remove elementos irrelevantes e limita tamanho."""

    # Remove múltiplos espaços e linhas vazias
    content = re.sub(r'\s+', ' ', content)

    # Remove scripts, estilos e elementos não-textuais
    soup = BeautifulSoup(content, 'html.parser')

    # Remove elementos comuns irrelevantes
    for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
        element.decompose()

    # Extrai texto
    text = soup.get_text(separator=' ', strip=True)

    # Limita por sentenças importantes (preserva contexto)
    sentences = re.split(r'[.!?]+', text)
    important_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:  # Remove frases muito curtas
            sentence_length = len(sentence.split())
            if current_length + sentence_length <= max_length:
                important_sentences.append(sentence)
                current_length += sentence_length
            else:
                break

    return '. '.join(important_sentences) + '.'

def calculate_relevance(content: str, query: str) -> float:
    """Calcula score de relevância baseado em palavras-chave."""

    query_words = set(query.lower().split())
    content_words = content.lower().split()

    # Conta ocorrências de palavras-chave
    matches = sum(1 for word in content_words if word in query_words)

    # Calcula densidade de palavras-chave
    density = matches / len(content_words) if content_words else 0

    # Bonus para posição inicial
    first_200_words = ' '.join(content_words[:200])
    early_matches = sum(1 for word in first_200_words.split() if word in query_words)

    return density + (early_matches * 0.1)

def select_best_contents(contents: List[Dict], max_total_tokens: int) -> List[Dict]:
    """Seleciona os melhores conteúdos sem ultrapassar limite de tokens."""

    # Ordena por relevância
    sorted_contents = sorted(contents, key=lambda x: x['score'], reverse=True)

    selected = []
    total_tokens = 0

    for content in sorted_contents:
        if total_tokens + content['length'] <= max_total_tokens:
            selected.append(content)
            total_tokens += content['length']
        else:
            # Adiciona parcial se couber um resumo
            remaining = max_total_tokens - total_tokens
            if remaining > 100:
                truncated = content['content'][:remaining * 5]  # Aproximação
                content['content'] = truncated
                selected.append(content)
            break

    return selected

def summarize_contents(contents: List[Dict], query: str) -> dict:
    """Sumariza os conteúdos selecionados de forma focada."""

    if not contents:
        return {"summary": None, "error": "Nenhum conteúdo relevante encontrado"}

    # Prepara prompt otimizado
    context_parts = []
    for i, item in enumerate(contents, 1):
        context_parts.append(
            f"Fonte {i}: {item['title']}\n"
            f"URL: {item['url']}\n"
            f"Trecho: {item['content'][:500]}...\n"
        )

    combined_context = "\n".join(context_parts)

    # Usa modelo mais barato e específico
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    prompt = f"""Analise os seguintes trechos de páginas web sobre: "{query}"

{combined_context}

Extraia apenas as informações mais relevantes e crie um resumo conciso e informativo.
Responda em português e cite as fontes quando relevante."""

    response = client.chat.completions.create(
        model="google/gemini-flash-1.5",  # Mais barato e eficiente
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    if response and response.choices:
        return {
            "summary": response.choices[0].message.content,
            "sources": [{"title": c["title"], "url": c["url"]} for c in contents],
            "total_sources": len(contents),
            "error": None
        }

if __name__ == "__main__":
    query = input("Digite sua consulta: ")
    result = web_fetch(
        query=query,
        n_sources=10,
        max_content_length=3000
    )

    if result["error"]:
        print("Erro:", result["error"])
    else:
        print("Resumo:", result["summary"])
        print("Fontes usadas:", len(result["sources"]))
