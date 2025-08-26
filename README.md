# ebook-generator — Geração de eBooks com IA, Pesquisa Web e Exportação para PDF

Cria eBooks completos (outline + introdução + capítulos) a partir de uma ideia inicial, com pesquisa web automática para dados atualizados e exportação final em Markdown e PDF com estilo CSS.

Recrutadores: este projeto demonstra integração de LLMs com function calling, orquestração de múltiplas APIs externas, scraping e processamento de texto, além de um pipeline completo de geração e publicação de conteúdo.

## Destaques técnicos (hard skills)
- Python moderno (tipagem, módulos, packaging simples) e organização por camadas
- Integração com LLM via OpenRouter (OpenAI SDK), usando:
	- Chat Completions
	- Function calling (tools) para executar funções externas sob demanda
	- Configuração do modelo e system prompt via JSON (separação de concerns)
	- Suporte a modelos Google Gemini via OpenRouter
- Engenharia de Prompt e contratos de resposta:
	- Respostas estruturadas em JSON e Markdown controladas por `response_format`
	- Prompts reutilizáveis e versionáveis em `config/*.json`
- Pesquisa e extração de conteúdo web:
	- SerpAPI para busca no Google
	- Requests + headers customizados
	- Trafilatura para extração de conteúdo relevante
	- BeautifulSoup para limpeza e saneamento
- Sumarização assistida por LLM com contexto e citação de fontes
- Geração de eBook end-to-end:
	- CLI interativa (`main.py`) para coletar requisitos
	- Geração de Outline, Introdução e Capítulos com densidade e ativos práticos
	- Composição final em Markdown
	- Conversão MD → HTML (ConvertAPI) → PDF (PDFEndpoint) com CSS customizado
- Boas práticas de robustez e DX:
	- Tratamento de erros de API (Auth, Connection, Rate/Generic)
	- Uso de variáveis de ambiente para segredos (OpenRouter, SerpAPI, PDF, ConvertAPI)
	- Logs informativos e mensagens orientadas ao usuário final

## Arquitetura e fluxo
1) Usuário fornece: título, ideia, público-alvo, tom/estilo (CLI).
2) Módulo LLM gera o outline com possibilidade de chamar `web_fetch` (function calling) para enriquecer dados.
3) Introdução gerada com copywriting persuasivo em Markdown.
4) Para cada capítulo, o modelo pode chamar `web_fetch` até 3x para buscar estatísticas/dados atuais; o texto resultante inclui checklists, frameworks e exemplos.
5) O conteúdo completo é salvo em `dist/<titulo>.md`.
6) Pipeline de exportação: Markdown → HTML (ConvertAPI) → PDF (PDFEndpoint) aplicando `ebook_style.css`.

Estrutura (simplificada):
- `main.py` — CLI e orquestração
- `ebook_tools/ebook_generator.py` — prompts e chamadas LLM (outline, introdução, capítulo)
- `ebook_tools/ebook_converter.py` — conversões MD→HTML→PDF
- `llm/llm_client.py` — cliente OpenRouter + function calling + tratamento de erros
- `llm/tool_functions.py` — `web_fetch`: SerpAPI, requests, trafilatura, BeautifulSoup, sumarização
- `config/*.json` — modelos, system prompts e formatos de resposta

## Competências demonstradas (mapa rápido)
- LLM Ops: OpenRouter, modelos Gemini, function calling, histórico de mensagens
- Prompt Engineering: system prompts modulares, contratos de saída (JSON/Markdown)
- APIs externas: SerpAPI, ConvertAPI, PDFEndpoint (auth, headers, payloads JSON)
- Web scraping/cleaning: requests, User-Agent, trafilatura, BeautifulSoup
- Processamento de texto: limpeza, relevância, sumarização, concatenação Markdown
- UX de linha de comando: fluxo guiado, mensagens e progresso
- Arquitetura de software: separação por camadas, configs em JSON, injeção de tools
- Segurança e config: variáveis de ambiente, chaves de API fora do código-fonte (recomendado)

## Como rodar localmente
Pré-requisitos:
- Python 3.10+
- Chaves de API: OpenRouter, SerpAPI, PDFEndpoint, ConvertAPI (todas possibilitam uso gratuito)

1) Instalar dependências
```bash
pip install -r requirements.txt
```

2) Configurar variáveis de ambiente (exemplo em bash)
```bash
export OPENROUTER_API_KEY="seu_token_openrouter"
export SERP_API_KEY="seu_token_serpapi"
export PDFENDPOINT_API_KEY="seu_token_pdfendpoint"
export CONVERTAPI_API_KEY="seu_token_convertapi"
```

3) Executar a CLI
```bash
python main.py
```

Saídas:
- Markdown: `dist/<TITULO_SEM_ESPACOS>.md`
- PDF: `dist/<TITULO_SEM_ESPACOS>.pdf`

## Configuração de modelos (configs)
- `config/generate_outline.json`: escolhe o modelo, system prompt e `response_format: json_object` para retornar um outline estruturado.
- `config/generate_introduction.json`: resposta em Markdown plain-text.
- `config/generate_chapter.json`: instruções para capítulos densos, ativos práticos e uso controlado de `web_fetch`.

---
Este repositório é focado em demonstrar integração de LLMs e engenharia de dados de texto ponta a ponta, pronto para evoluir para um produto de geração de conteúdo com qualidade de produção.
--
Feito com ❤️ por Miguel Filippo Rocha Calhabeu
