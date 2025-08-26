import json
import os
from openai import OpenAI, APIError, AuthenticationError, APIConnectionError
from llm.tool_functions import *

class LLM:
    """
    Uma classe para interagir com um modelo de linguagem (LLM) através da API da OpenAI/OpenRouter.
    Ela lida com a configuração do modelo a partir de um arquivo JSON e faz requisições,
    incluindo um tratamento de erros robusto.
    """
    def __init__(self):
        """
        Inicializa o cliente da API e valida a existência da chave de API.
        """
        # Documentação: Verifica se a variável de ambiente com a chave da API existe.
        # Se não existir, levanta um erro claro para o usuário.
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("A variável de ambiente 'OPENROUTER_API_KEY' não foi definida.")

        # Documentação: Inicializa o cliente da OpenAI com a URL base e a chave.
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = None
        self.system_prompt = None
        self.response_format = None

    def config_model(self, json_file: str) -> bool:
        """
        Carrega a configuração do modelo a partir de um arquivo JSON.

        Args:
            json_file (str): O caminho para o arquivo de configuração JSON.

        Returns:
            bool: True se a configuração foi carregada com sucesso, False caso contrário.
        """
        try:
            # Documentação: Abre e lê o arquivo de configuração.
            with open(json_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Documentação: Obtém os valores do dicionário. O método .get() é seguro,
            # pois retorna None se a chave não existir, evitando erros.
            self.model = config.get("model")
            self.system_prompt = config.get("system_prompt")

            # CORREÇÃO: Atribui o dicionário diretamente, sem converter para string.
            self.response_format = config.get("response_format")

            # Documentação: Valida se as configurações essenciais foram carregadas.
            if not self.model or not self.system_prompt:
                print("Erro: 'model' e 'system_prompt' são campos obrigatórios no arquivo de configuração.")
                return False

            return True

        # Documentação: Tratamento de erro específico se o arquivo não for encontrado.
        except FileNotFoundError:
            print(f"Erro: O arquivo de configuração '{json_file}' não foi encontrado.")
            return False
        # Documentação: Tratamento de erro específico se o JSON for inválido.
        except json.JSONDecodeError:
            print(f"Erro: O arquivo '{json_file}' não contém um JSON válido.")
            return False
        # Documentação: Captura qualquer outro erro inesperado durante a leitura.
        except Exception as e:
            print(f"Erro inesperado ao carregar a configuração: {e}")
            return False

    def make_request(
        self,
        prompt: str,
        tools: list[dict[str, any]] = None,
        available_functions: dict[str, callable] = None
    ) -> str | None:
        """
        Envia um prompt para o modelo configurado e retorna a resposta.
        Suporta function calling com tools.

        Args:
            prompt (str): O prompt do usuário a ser enviado para o modelo.
            tools (List[Dict], optional): Lista de tools/functions disponíveis para o modelo.
                Formato esperado:
                [{
                    "type": "function",
                    "function": {
                        "name": "nome_da_funcao",
                        "description": "Descrição da função",
                        "parameters": {
                            "type": "object",
                            "properties": {...},
                            "required": [...]
                        }
                    }
                }]
            available_functions (Dict[str, Callable], optional): Dicionário mapeando nomes de
                funções para suas implementações reais. Exemplo: {"get_weather": get_weather_function}

        Returns:
            str | None: O conteúdo da resposta do modelo, ou None se ocorrer um erro.
        """
        if not self.model:
            print("Erro: O modelo não foi configurado. Chame o método config_model() primeiro.")
            return None

        try:
            # Prepara as mensagens iniciais
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]

            extra_body={
                "provider": {
                    "sort": "throughput"
                }
            }

            # Primeira chamada: Envia prompt e tools para o modelo
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                extra_body=extra_body,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                response_format=({"type": self.response_format} if self.response_format else None)
            )

            # Processa a resposta do modelo
            response_message = response.choices[0].message

            # Se não há tool calls, retorna a resposta direta
            if not response_message.tool_calls:
                return response_message.content

            # Adiciona a resposta do modelo ao histórico
            messages.append(response_message)

            # Processa os tool calls (function calls)
            if response_message.tool_calls and available_functions:
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name

                    # Verifica se a função está disponível
                    if function_name not in available_functions:
                        print(f"Erro: Função '{function_name}' não encontrada em available_functions")
                        continue

                    function_to_call = available_functions[function_name]

                    try:
                        # Parse dos argumentos
                        function_args = json.loads(tool_call.function.arguments)

                        # Executa a função
                        print(f"Chamando função: {function_name} com args: {function_args}")
                        function_response = function_to_call(**function_args)

                        # Adiciona o resultado ao histórico de mensagens
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": str(function_response)
                        })

                    except json.JSONDecodeError as e:
                        print(f"Erro ao decodificar argumentos da função {function_name}: {e}")
                        continue
                    except Exception as e:
                        print(f"Erro ao executar função {function_name}: {e}")
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": f"Erro: {str(e)}"
                        })

                # Segunda chamada: Envia os resultados das funções de volta ao modelo
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format=({"type": self.response_format} if self.response_format else None)
                )

                return final_response.choices[0].message.content

            return response_message.content

        except AuthenticationError as e:
            print(f"Erro de autenticação: Verifique sua API key. Detalhes: {e}")
            return None
        except APIConnectionError as e:
            print(f"Erro de conexão com a API: Verifique sua conexão à internet. Detalhes: {e}")
            return None
        except APIError as e:
            print(f"Erro na API do OpenAI/OpenRouter: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao fazer a requisição: {e}")
            return None
