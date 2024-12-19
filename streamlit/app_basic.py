import streamlit as st
import requests
import plotly.graph_objects as go
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI

# Configuração inicial
load_dotenv()
st.set_page_config(page_title="⚽ Análise de Partida", layout="wide")

# Configurações
API_BASE_URL = "http://localhost:8000/api/v1"
MATCH_ID = 3788741  # Turquia vs Itália
PLAYER_ID = 11086.0  # Burak Yilmaz

# Cliente OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_match_data() -> Dict:
    """Obtém dados da partida"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}")
        response.raise_for_status()
        data = response.json()
        st.write("Debug - Dados da partida:", data)  # Debug
        return data
    except Exception as e:
        st.error(f"Erro ao obter dados da partida: {str(e)}")
        return {}

def get_player_data() -> Dict:
    """Obtém dados do jogador"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/player/{PLAYER_ID}")
        response.raise_for_status()
        data = response.json()
        st.write("Debug - Dados do jogador:", data)  # Debug
        return data
    except Exception as e:
        st.error(f"Erro ao obter dados do jogador: {str(e)}")
        return {}

def get_match_analysis(style: str = "formal") -> Dict:
    """Obtém análise da partida"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/analysis?style={style}")
        response.raise_for_status()
        data = response.json()
        st.write("Debug - Análise:", data)  # Debug
        return data
    except Exception as e:
        st.error(f"Erro ao obter análise: {str(e)}")
        return {}

def main():
    st.title("⚽ Análise de Partida de Futebol")
    
    # Debug - Mostrar status da API
    st.write("Tentando conectar à API...")
    
    # 1. Dados da Partida
    match_data = get_match_data()
    if match_data:
        # Cabeçalho da partida
        st.header("Informações da Partida")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(match_data.get('home_team', 'Time da Casa'))
        with col2:
            st.subheader(match_data.get('score', '0 - 0'))
        with col3:
            st.subheader(match_data.get('away_team', 'Time Visitante'))
        
        # Eventos
        st.subheader("Eventos da Partida")
        events = match_data.get('events', [])
        for event in events:
            st.write(f"{event.get('minute', '?')}' - {event.get('type', '?')} - {event.get('team', '?')}")
    
    # 2. Dados do Jogador
    st.markdown("---")
    st.header("Análise do Jogador")
    player_data = get_player_data()
    
    if player_data and 'info' in player_data:
        info = player_data['info']
        stats = player_data.get('statistics', {})
        
        st.subheader(info.get('player_name', 'Jogador'))
        st.write(f"Time: {info.get('team', 'N/A')}")
        
        if stats:
            col1, col2 = st.columns(2)
            with col1:
                passes = stats.get('passes', {})
                st.metric("Passes Totais", passes.get('total', 0))
                st.metric("Passes Completos", passes.get('successful', 0))
            
            with col2:
                shots = stats.get('shots', {})
                st.metric("Finalizações", shots.get('total', 0))
                st.metric("Gols", shots.get('goals', 0))
    
    # 3. Análise da Partida
    st.markdown("---")
    st.header("Análise da Partida")
    
    style = st.selectbox("Estilo da Análise", ["formal", "humoristico", "tecnico"])
    if st.button("Gerar Análise"):
        analysis = get_match_analysis(style)
        if analysis and 'analysis' in analysis:
            st.write(analysis['analysis'])

if __name__ == "__main__":
    main()
