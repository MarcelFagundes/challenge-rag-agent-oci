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
