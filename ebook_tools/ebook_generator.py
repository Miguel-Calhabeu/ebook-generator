import json
from llm.llm_client import LLM
from llm.tool_functions import web_fetch

def generate_ebook_outline(ideia_inicial: str, publico_alvo: str, tom_estilo: str) -> dict | None:
    """
    Gera um esboço de eBook com base na ideia inicial, público-alvo e tom de estilo.

    Args:
        ideia_inicial (str): A ideia inicial para o eBook.
        publico_alvo (str): O público-alvo do eBook.
        tom_estilo (str): O tom e estilo desejados para o eBook.

    Returns:
        dict: Um dicionário contendo o esboço do eBook.
    """

    user_prompt = f"""
    Ideia inicial: {ideia_inicial}
    Público-alvo: {publico_alvo}
    Tom e estilo: {tom_estilo}
    """

    # Cria uma instância da classe LLM
    try:
        llm = LLM()
    except ValueError as e:
        raise ValueError("Erro ao inicializar a LLM.")

    # Configura a tool de web fetching
    tools = [{
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Busca informações atualizadas na web sobre um tópico específico",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Consulta de busca"},
                    "n_sources": {"type": "integer", "description": "Número de fontes", "default": 3},
                    "max_content_length": {"type": "integer", "description": "Tamanho máximo do conteúdo", "default": 5000}
                },
                "required": ["query"]
            }
        }
    }]

    available_functions = {"web_fetch": web_fetch}

    # Carrega a configuração do modelo a partir do arquivo JSON
    if llm.config_model("config/generate_outline.json"):
        # Se a configuração foi bem-sucedida, faz uma pergunta
        response = llm.make_request(user_prompt, tools=tools, available_functions=available_functions)
        print(response)

        if response:
            try:
                response = json.loads(response)
                return response
            except json.JSONDecodeError:
                raise ValueError(f"Erro ao decodificar a resposta JSON: {response}")
        else:
            raise ValueError("Erro na requisição ao modelo.")
    else:
        raise ValueError("Erro ao configurar o modelo LLM a partir do arquivo JSON.")

def generate_ebook_introduction(ebook_outline: dict) -> str | None:
    """
    Gera uma introdução para o eBook com base no esboço fornecido.

    Args:
        ebook_outline (dict): O esboço do eBook.

    Returns:
        str: A introdução do eBook.
    """

    user_prompt = f"""
    Escreva uma introdução para o seguinte esboço de eBook:
    {json.dumps(ebook_outline, indent=2, ensure_ascii=False)}
    """

    # Cria uma instância da classe LLM
    try:
        llm = LLM()
    except ValueError as e:
        raise ValueError("Erro ao inicializar a LLM.")

    # Carrega a configuração do modelo a partir do arquivo JSON
    if llm.config_model("config/generate_introduction.json"):
        # Se a configuração foi bem-sucedida, faz uma pergunta
        response = llm.make_request(user_prompt)

        if response:
              return response
        else:
            raise ValueError("Erro na requisição ao modelo.")
    else:
        raise ValueError("Erro ao configurar o modelo LLM a partir do arquivo JSON.")

def generate_ebook_chapter(ebook_outline: dict, chapter_number: int) -> str | None:
    """
    Gera um capítulo para o eBook com base no esboço fornecido.

    Args:
        ebook_outline (dict): O esboço do eBook.
        chapter_number (int): O número do capítulo a ser gerado.

    Returns:
        str: O capítulo do eBook.
    """

    user_prompt = f"""
    Escreva um capítulo para o seguinte esboço de eBook:
    {json.dumps(ebook_outline, indent=2, ensure_ascii=False)}
    Capítulo: {chapter_number}
    """

    # Cria uma instância da classe LLM
    try:
        llm = LLM()
    except ValueError as e:
        raise ValueError("Erro ao inicializar a LLM.")

    # Configura a tool de web fetching
    tools = [{
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Busca informações atualizadas na web sobre um tópico específico",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Consulta de busca"},
                    "n_sources": {"type": "integer", "description": "Número de fontes", "default": 3},
                    "max_content_length": {"type": "integer", "description": "Tamanho máximo do conteúdo", "default": 5000}
                },
                "required": ["query"]
            }
        }
    }]

    available_functions = {"web_fetch": web_fetch}

    # Carrega a configuração do modelo a partir do arquivo JSON
    if llm.config_model("config/generate_chapter.json"):
        # Se a configuração foi bem-sucedida, faz uma pergunta
        response = llm.make_request(user_prompt, tools=tools, available_functions=available_functions)

        if response:
              return response
        else:
            raise ValueError("Erro na requisição ao modelo.")
    else:
        raise ValueError("Erro ao configurar o modelo LLM a partir do arquivo JSON.")

if __name__ == "__main__":
    pass
