import streamlit as st
import pandas as pd
from utils.data_loader import load_match_data
from utils.visualization import create_player_stats_plot

st.set_page_config(
    page_title="Análise de Partidas de Futebol",
    page_icon="⚽",
    layout="wide"
)

def main():
    st.title("⚽ Análise de Partidas de Futebol")
    
    st.sidebar.header("Configurações")
    match_id = st.sidebar.text_input("ID da Partida", "")
    
    if match_id:
        try:
            # Placeholder para futura integração com a API
            st.info("Esta é uma versão inicial. Integrações com API serão adicionadas em breve.")
            
            # Tabs para diferentes análises
            tab1, tab2, tab3 = st.tabs(["Resumo da Partida", "Perfil dos Jogadores", "Narrativas"])
            
            with tab1:
                st.header("Resumo da Partida")
                st.write("Funcionalidade em desenvolvimento...")
            
            with tab2:
                st.header("Perfil dos Jogadores")
                st.write("Funcionalidade em desenvolvimento...")
            
            with tab3:
                st.header("Narrativas")
                st.write("Funcionalidade em desenvolvimento...")
                
        except Exception as e:
            st.error(f"Erro ao carregar os dados: {str(e)}")
    else:
        st.info("👈 Por favor, insira um ID de partida para começar a análise.")

if __name__ == "__main__":
    main()
