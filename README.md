# Assistente Virtual para Banco Digital (RAG) — PagFácil Bank

Agente de IA que responde perguntas em linguagem natural sobre a documentação para
clientes de um banco digital fictício, o **PagFácil Bank**, cobrindo:

- Política de privacidade e proteção de dados (LGPD)
- Termos e condições de uso
- Perguntas frequentes sobre transações e limites (Pix, TED, cartão)
- Política de segurança e prevenção de fraudes
- Tarifas e comissões do serviço

Toda a documentação está em `data/pagfacil_docs.pdf`. O agente usa RAG
(Retrieval-Augmented Generation) para responder **somente com base no conteúdo do
documento**, evitando "inventar" políticas ou valores que não existem.

🔗 **Deploy oficial (OCI):** `<https://challenge-rag-agent-oci-kkhcmyeamai76mgf79tccm.streamlit.app/>`

📸 **Screenshot da aplicação rodando:**

![Tela inicial do agente funcionando](print/i3_screenshot_2026-08-05-16-20-06.png)
![Segunda tela do agente funcionando](print/i3_screenshot_2026-08-05-16-20-11.png)

---

## 1. Arquitetura

```
                         ┌─────────────────────────┐
                         │        Cliente          │
                         │  (navegador / browser)  │
                         └────────────┬────────────┘
                                      │ HTTP (porta 8501)
                                      ▼
                         ┌─────────────────────────┐
                         │  Streamlit (app.py)     │
                         │  Interface de chat      │
                         └────────────┬────────────┘
                                      ▼
                         ┌─────────────────────────┐
                         │ Agente LangChain        │
                         │        (agent.py)       │
                         └────────────┬────────────┘
                                      ▼
                    ┌───────────────────────────────────┐
                    │  Tool: consultar_documentacao     │
                    │  Retrieval (FAISS + embeddings)   │
                    │  → data/pagfacil_docs.pdf         │
                    │    (privacidade, termos, FAQ,     │
                    │     segurança/fraude, tarifas)    │
                    └────────────────┬──────────────────┘
                                     ▼
                         ┌─────────────────────────┐
                         │   LLM (Claude / GPT /   │
                         │   Gemini, via API)      │
                         └─────────────────────────┘
```

**Fluxo:**
1. O cliente faz uma pergunta na interface web (Streamlit).
2. Um agente ReAct (LangChain) aciona a ferramenta `consultar_documentacao`.
3. A ferramenta busca os trechos mais relevantes do PDF em um índice vetorial FAISS
   (embeddings locais via `sentence-transformers`, sem custo de API).
4. O LLM (Claude, GPT ou Gemini — configurável) recebe apenas esses trechos como
   contexto e formula a resposta final em português, sem extrapolar do que está
   documentado.

---

## 2. Tecnologias usadas

| Camada                 | Tecnologia                                                 |
|------------------------|------------------------------------------------------------|
| Linguagem              | Python 3.11 ou 3.12                                        |
| Orquestração do agente | LangChain (`create_react_agent`, `AgentExecutor`)          |
| Leitura de PDF         | `pypdf` / `PyPDFLoader`                                    |
| Embeddings             | `sentence-transformers` (all-MiniLM-L6-v2), local          |
| Índice vetorial        | FAISS                                                      |
| LLM                    | Gemini (padrão, grátis) — configurável para Claude ou GPT  |
| Interface              | Streamlit                                                  |
| Nuvem (deploy de teste)| Streamlit Community Cloud                                  |

---
