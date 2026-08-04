"""
app.py
------
Interface web mínima (Streamlit) para o agente de IA.

Rodar localmente:
    streamlit run app.py

Rodar na OCI:
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
"""

import streamlit as st
from agent import build_agent

st.set_page_config(page_title="Agente PagFácil Bank", page_icon="🏦")
st.title("🏦 Assistente Virtual - PagFácil Bank")
st.caption(
    "Pergunte sobre privacidade e proteção de dados, termos de uso, limites de transações, "
    "segurança/prevenção de fraudes ou tarifas do banco."
)

if "executor" not in st.session_state:
    with st.spinner("Carregando agente (indexando a documentação)..."):
        st.session_state.executor = build_agent()

if "historico" not in st.session_state:
    st.session_state.historico = []

for pergunta, resposta in st.session_state.historico:
    with st.chat_message("user"):
        st.write(pergunta)
    with st.chat_message("assistant"):
        st.write(resposta)

pergunta = st.chat_input("Digite sua pergunta...")
if pergunta:
    with st.chat_message("user"):
        st.write(pergunta)
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            resultado = st.session_state.executor.invoke({"input": pergunta})
            resposta = resultado["output"]
            st.write(resposta)
    st.session_state.historico.append((pergunta, resposta))
