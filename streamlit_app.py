import streamlit as st
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from datetime import datetime
from io import StringIO

# Configurar logging com StringIO
log_stream = StringIO()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=log_stream
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
logger.info("Variáveis de ambiente carregadas")

# Configurar Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')
logger.info("Modelo Gemini configurado")

# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1"
logger.info(f"API base URL configurada: {API_BASE_URL}")

def get_match_data(match_id: int) -> Dict[str, Any]:
    """Busca dados completos de uma partida"""
    try:
        # Buscar dados brutos
        response = requests.get(f"{API_BASE_URL}/matches/{match_id}")
        if response.status_code == 200:
            match_data = response.json()
            
            # Buscar sumário
            summary_response = requests.get(f"{API_BASE_URL}/matches/{match_id}/summary")
            if summary_response.status_code == 200:
                match_data.update(summary_response.json())
            
            logger.info("Dados da partida carregados com sucesso")
            return match_data
        logger.error(f"Erro ao buscar dados: {response.status_code}")
    except Exception as e:
        logger.error(f"Exceção ao buscar dados: {str(e)}")
    return None

def get_match_narrative(match_id: int, style: str) -> str:
    """Busca narrativa da partida em um estilo específico"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/matches/{match_id}/analysis",
            params={"style": style}
        )
        if response.status_code == 200:
            return response.json().get("analysis", "")
    except Exception as e:
        logger.error(f"Erro ao buscar narrativa: {str(e)}")
    return ""

def display_match_summary(match_data: Dict[str, Any]):
    """Exibe o resumo da partida de forma organizada"""
    if not match_data:
        return
    
    st.subheader("⚽ Inglaterra vs Colômbia - Copa do Mundo 2018")
    st.write("Oitavas de Final - 03/07/2018")
    
    # Placar
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Inglaterra", "")
    with col2:
        if 'goals' in match_data:
            england_goals = len([g for g in match_data['goals'] if g['team'] == 'England'])
            colombia_goals = len([g for g in match_data['goals'] if g['team'] == 'Colombia'])
            st.metric("Placar", f"{england_goals} - {colombia_goals}")
    with col3:
        st.metric("Colômbia", "")
    
    # Timeline dos gols
    if 'goals' in match_data:
        st.subheader("⚽ Gols da Partida")
        for goal in match_data['goals']:
            progress = min(1.0, goal['minute'] / 120.0)
            st.progress(progress)
            st.markdown(f"""
            **{goal['minute']}'** - ⚽ Gol de **{goal['scorer']}** ({goal['team']})
            {f"*Assistência: {goal['assist']}*" if goal['assist'] else ""}
            """)

def display_player_stats(match_data: Dict[str, Any], player_name: str):
    """Exibe estatísticas detalhadas de um jogador"""
    events = [e for e in match_data.get('events', []) if e.get('player') == player_name]
    
    if not events:
        st.warning(f"Não foram encontradas estatísticas para {player_name}")
        return

    # Calcular estatísticas
    stats = {
        'passes': len([e for e in events if e.get('type') == 'Pass']),
        'shots': len([e for e in events if e.get('type') == 'Shot']),
        'goals': len([e for e in events if e.get('type') == 'Shot' and e.get('shot_outcome') == 'Goal']),
        'tackles': len([e for e in events if e.get('type') == 'Duel']),
        'first_half': len([e for e in events if e.get('minute', 0) <= 45]),
        'second_half': len([e for e in events if e.get('minute', 0) > 45])
    }

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Passes", stats['passes'])
    with col2:
        st.metric("Finalizações", stats['shots'])
    with col3:
        st.metric("Gols", stats['goals'])

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        fig_events = go.Figure(data=[go.Pie(
            labels=['Primeiro Tempo', 'Segundo Tempo'],
            values=[stats['first_half'], stats['second_half']],
            hole=.3
        )])
        fig_events.update_layout(title="Distribuição de Eventos por Tempo")
        st.plotly_chart(fig_events)
    
    with col2:
        fig_stats = go.Figure(data=[
            go.Bar(name='Total', x=['Passes', 'Finalizações', 'Desarmes'],
                   y=[stats['passes'], stats['shots'], stats['tackles']])
        ])
        fig_stats.update_layout(title="Estatísticas do Jogador")
        st.plotly_chart(fig_stats)

# Interface Streamlit
st.title("⚽ Análise de Partidas de Futebol")

# Barra lateral
with st.sidebar:
    st.header("Seleção de Partida")
    match_id = 7585  # Inglaterra vs Colômbia
    if st.button("Carregar Dados"):
        match_data = get_match_data(match_id)
        if match_data:
            st.session_state['match_data'] = match_data
            st.success("Dados carregados com sucesso!")
        else:
            st.error("Erro ao carregar dados da partida")

    # Seleção de modo de visualização
    if 'match_data' in st.session_state:
        st.header("Modo de Visualização")
        view_mode = st.radio(
            "Escolha o que deseja ver:",
            ["Resumo da Partida", "Estatísticas de Jogador", "Narrativas", "Chat"]
        )
        st.session_state['view_mode'] = view_mode

# Área principal
if 'match_data' in st.session_state:
    view_mode = st.session_state.get('view_mode', "Resumo da Partida")
    
    if view_mode == "Resumo da Partida":
        display_match_summary(st.session_state['match_data'])
    
    elif view_mode == "Estatísticas de Jogador":
        st.header("Estatísticas de Jogadores")
        players = set(
            e.get('player', '') 
            for e in st.session_state['match_data'].get('events', []) 
            if e.get('player')
        )
        players = sorted(list(players))
        
        if players:
            selected_player = st.selectbox("Selecione um jogador", players)
            if selected_player:
                display_player_stats(st.session_state['match_data'], selected_player)
        else:
            st.warning("Nenhum jogador encontrado nos dados da partida")
    
    elif view_mode == "Narrativas":
        st.header("Narrativas da Partida")
        style = st.selectbox(
            "Escolha o estilo de narração",
            ["formal", "humoristico", "tecnico"],
            format_func=lambda x: {
                "formal": "Formal (Análise objetiva)",
                "humoristico": "Humorístico (Narração descontraída)",
                "tecnico": "Técnico (Análise tática detalhada)"
            }[x]
        )
        
        if st.button("Gerar Narrativa"):
            with st.spinner("Gerando narração..."):
                narrative = get_match_narrative(st.session_state['match_id'], style)
                st.markdown(narrative)
    
    elif view_mode == "Chat":
        st.header("Chat Interativo")
        st.write("""
        Faça perguntas sobre a partida! Exemplos:
        - Quem marcou os gols?
        - Quantos passes foram dados no primeiro tempo?
        - Qual jogador teve mais finalizações?
        """)
        
        # Inicializar histórico de mensagens
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Mostrar histórico
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input do usuário
        if prompt := st.text_input("Faça sua pergunta sobre a partida"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                events = st.session_state['match_data'].get('events', [])
                context = f"""
                Partida: Inglaterra vs Colômbia - Copa do Mundo 2018
                
                Eventos principais:
                {[f"{e.get('type')} por {e.get('player')} ({e.get('team')}) no minuto {e.get('minute')}"
                  for e in events if e.get('type') in ['Goal', 'Shot', 'Card']]}
                
                Pergunta: {prompt}
                """
                response = model.generate_content(context)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

# Área de logs
if st.checkbox("Mostrar Logs"):
    st.text("Logs do sistema:")
    st.code(log_stream.getvalue())

# Footer
st.markdown("---")
st.markdown("Desenvolvido para AT - Desenvolvimento de Data Driven Apps")
