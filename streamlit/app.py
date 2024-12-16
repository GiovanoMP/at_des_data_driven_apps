import streamlit as st
import pandas as pd
from utils.data_loader import load_match_data
from utils.visualization import create_player_stats_plot
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

# Configuração da página Streamlit
st.set_page_config(
    page_title="Análise de Partidas de Futebol",
    page_icon="⚽",
    layout="wide"
)

def process_chat_input(user_input: str, chat_history: list) -> str:
    """
    Processa a entrada do usuário usando o Gemini e retorna a resposta.
    """
    try:
        response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        return f"Erro ao processar mensagem: {str(e)}"

def main():
    st.title("⚽ Análise de Partidas de Futebol")
    
    # Sidebar para configurações
    st.sidebar.header("Configurações")
    match_id = st.sidebar.text_input("ID da Partida", "")
    
    # Inicializa o histórico do chat se não existir
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Interface principal com tabs
    tab1, tab2, tab3 = st.tabs(["Resumo da Partida", "Perfil dos Jogadores", "Chat Interativo"])
    
    if match_id:
        try:
            with tab1:
                st.header("Resumo da Partida")
                if st.button("Gerar Resumo"):
                    with st.spinner("Gerando resumo..."):
                        # Placeholder para integração com API
                        st.info("Funcionalidade em desenvolvimento...")
            
            with tab2:
                st.header("Perfil dos Jogadores")
                st.write("Funcionalidade em desenvolvimento...")
            
            with tab3:
                st.header("Chat Interativo com Gemini")
                
                # Área de chat
                for message in st.session_state.chat_history:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
                
                # Input do usuário
                user_input = st.chat_input("Faça uma pergunta sobre a partida...")
                if user_input:
                    # Adiciona mensagem do usuário ao histórico
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    # Processa a resposta
                    with st.chat_message("assistant"):
                        response = process_chat_input(user_input, st.session_state.chat_history)
                        st.write(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                
        except Exception as e:
            st.error(f"Erro ao carregar os dados: {str(e)}")
    else:
        st.info("👈 Por favor, insira um ID de partida para começar a análise.")

if __name__ == "__main__":
    main()
