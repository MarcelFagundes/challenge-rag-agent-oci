"""
agent.py
--------
Agente de IA que responde perguntas sobre a documentação de um banco digital
fictício (PagFácil Bank), usando RAG (Retrieval-Augmented Generation) com LangChain.

Documento-base (data/pagfacil_docs.pdf) cobre:
  1. Política de privacidade e proteção de dados
  2. Termos e condições de uso
  3. Perguntas frequentes sobre transações e limites
  4. Política de segurança e prevenção de fraudes
  5. Tarifas e comissões do serviço
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"

# Lista de documentos PDF que compõem a base de conhecimento do banco digital.
# Adicione mais arquivos aqui se quiser separar os temas em documentos distintos.
PDF_PATHS = [
    DATA_DIR / "pagfacil_docs.pdf",
]


def get_llm():
    """Cria o LLM configurado via variável de ambiente LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        client_options_timeout = {
            "timeout": None,
        }
        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL", "gemini-3.1-flash-lite"),
            default_options={"timeout": 120.0}, 
            max_retries=3,
            temperature=0,
        )
    # elif provider == "anthropic":
    #     from langchain_anthropic import ChatAnthropic
    #     return ChatAnthropic(
    #         model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
    #         temperature=0,
    #     )
    # elif provider == "openai":
    #     from langchain_openai import ChatOpenAI
    #     return ChatOpenAI(
    #         model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    #         temperature=0,
    #     )
    else:
        raise ValueError(f"LLM_PROVIDER desconhecido: {provider}")


def build_retriever():
    """Carrega todos os PDFs em PDF_PATHS, divide em chunks e cria um índice FAISS."""
    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)

    for pdf_path in PDF_PATHS:
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        chunks = splitter.split_documents(pages)
        all_chunks.extend(chunks)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(all_chunks, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 4})


def build_agent():
    """Monta o agente com a ferramenta de consulta à documentação (RAG)."""
    llm = get_llm()
    retriever = build_retriever()

    def consultar_documentacao(pergunta: str) -> str:
        docs = retriever.invoke(pergunta)
        contexto = "\n\n".join(d.page_content for d in docs)
        prompt = (
            "Você é um assistente de atendimento de um banco digital. Responda a pergunta "
            "abaixo usando SOMENTE as informações do contexto fornecido (política de "
            "privacidade, termos de uso, FAQ de transações e limites, política de segurança "
            "e prevenção de fraudes, e tarifas). Se a resposta não estiver no contexto, diga "
            "claramente que não encontrou essa informação na documentação e sugira contato "
            "com o suporte.\n\n"
            f"Contexto:\n{contexto}\n\nPergunta: {pergunta}"
        )
        return llm.invoke(prompt).content

    tools = [
        Tool(
            name="consultar_documentacao",
            func=consultar_documentacao,
            description=(
                "Use esta ferramenta para responder QUALQUER pergunta de um cliente sobre o "
                "banco digital: privacidade e proteção de dados, termos e condições de uso, "
                "limites e prazos de transações (Pix, TED, cartão), segurança e prevenção de "
                "fraudes, ou tarifas e comissões. A entrada deve ser a pergunta em linguagem "
                "natural."
            ),
        ),
    ]

    react_prompt = PromptTemplate.from_template(
        """Você é um assistente de atendimento de um banco digital, que responde de forma clara,
objetiva e em português, usando as ferramentas disponíveis para consultar a documentação oficial.

Ferramentas disponíveis:
{tools}

Use o seguinte formato:

Question: a pergunta de entrada
Thought: pense sobre qual ferramenta usar
Action: o nome da ferramenta, uma de [{tool_names}]
Action Input: a entrada para a ferramenta
Observation: o resultado da ferramenta
... (repita Thought/Action/Action Input/Observation quantas vezes for necessário)
Thought: agora sei a resposta final
Final Answer: a resposta final, clara e em português

Question: {input}
Thought: {agent_scratchpad}"""
    )

    agent = create_react_agent(llm, tools, react_prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
    )
    return executor


def ask(pergunta: str) -> str:
    """Função utilitária: faz uma pergunta ao agente e devolve a resposta final."""
    executor = build_agent()
    result = executor.invoke({"input": pergunta})
    return result["output"]


if __name__ == "__main__":
    perguntas_exemplo = [
        "Qual é o limite de transferência via Pix durante a noite?",
        "Quais são as tarifas para saque em caixa eletrônico?",
        "O banco pode me pedir a senha por telefone?",
        "Quanto tempo tenho para contestar uma transação fraudulenta?",
    ]
    for p in perguntas_exemplo:
        print(f"\nPergunta: {p}")
        print(f"Resposta: {ask(p)}")
