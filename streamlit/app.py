import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
import json

# Configurações da página
st.set_page_config(
    page_title="Análise de Partidas de Futebol",
    page_icon="⚽",
    layout="wide"
)

# Variáveis globais
API_URL = "http://localhost:8000/api/v1"

def get_match_data(match_id: int) -> Dict[str, Any]:
    """Obtém os dados de uma partida específica."""
    try:
        response = requests.get(f"{API_URL}/matches/{match_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter dados da partida: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return None

def get_match_summary(match_id: int) -> Dict[str, Any]:
    """Obtém o resumo de uma partida."""
    try:
        response = requests.get(f"{API_URL}/matches/{match_id}/summary")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter resumo da partida: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return None

def get_match_narrative(match_id: int, style: str) -> str:
    """Obtém a narrativa de uma partida."""
    try:
        response = requests.get(
            f"{API_URL}/matches/{match_id}/narrative",
            params={"style": style}
        )
        if response.status_code == 200:
            return response.json()["narrative"]
        else:
            st.error(f"Erro ao obter narrativa: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return None

def get_player_profile(match_id: int, player_id: int, include_analysis: bool = False) -> Dict[str, Any]:
    """Obtém o perfil de um jogador."""
    try:
        response = requests.get(
            f"{API_URL}/matches/{match_id}/player/{player_id}",
            params={"include_analysis": include_analysis}
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro ao obter perfil do jogador: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {str(e)}")
        return None

def display_match_summary(summary: Dict[str, Any]):
    """Exibe o resumo da partida de forma organizada."""
    info = summary["match_info"]
    events = summary["key_events"]
    
    # Informações básicas da partida
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Placar", info["score"])
    with col2:
        st.metric("Data", info["date"])
    with col3:
        st.metric("Estádio", info["stadium"])
    
    # Eventos principais
    st.subheader("Gols")
    for goal in events["goals"]:
        st.write(f"⚽ {goal['minute']}' - {goal['scorer']} ({goal['team']})")
        if goal["assist"]:
            st.write(f"   🅰️ Assistência: {goal['assist']}")
    
    st.subheader("Cartões")
    for card in events["cards"]:
        emoji = "🟨" if card["card_type"].lower() == "yellow" else "🟥"
        st.write(f"{emoji} {card['minute']}' - {card['player']} ({card['team']})")
    
    st.subheader("Substituições")
    for sub in events["substitutions"]:
        st.write(f"🔄 {sub['minute']}' - {sub['team']}")
        st.write(f"   ↪️ Entrou: {sub['player_in']}")
        st.write(f"   ↩️ Saiu: {sub['player_out']}")

def display_player_profile(profile: Dict[str, Any]):
    """Exibe o perfil do jogador de forma organizada."""
    info = profile["info"]
    stats = profile["statistics"]
    
    st.subheader(f"{info['player_name']} - {info['team']}")
    
    # Estatísticas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Passes Completos", f"{stats['passes']['successful']}/{stats['passes']['total']}")
    with col2:
        st.metric("Gols", f"{stats['shots']['goals']}/{stats['shots']['total']} chutes")
    with col3:
        st.metric("Desarmes", stats['tackles'])
    with col4:
        st.metric("Minutos Jogados", stats['minutes_played'])
    
    if "analysis" in profile:
        st.subheader("Análise Técnica")
        st.write(profile["analysis"])

def main():
    st.title("⚽ Análise de Partidas de Futebol")
    
    # Input da partida
    match_id = st.number_input("ID da Partida", min_value=1, value=7298)
    
    if st.button("Analisar Partida"):
        # Obter e exibir resumo da partida
        summary = get_match_summary(match_id)
        if summary:
            st.header("Resumo da Partida")
            display_match_summary(summary)
            
            # Gerar narrativa
            st.header("Narrativa da Partida")
            style = st.selectbox(
                "Estilo da Narrativa",
                ["formal", "humorous", "technical"],
                format_func=lambda x: {
                    "formal": "Formal",
                    "humorous": "Humorístico",
                    "technical": "Técnico"
                }[x]
            )
            
            if st.button("Gerar Narrativa"):
                narrative = get_match_narrative(match_id, style)
                if narrative:
                    st.write(narrative)
            
            # Análise de jogador
            st.header("Análise de Jogador")
            player_id = st.number_input("ID do Jogador", min_value=1)
            include_analysis = st.checkbox("Incluir análise detalhada")
            
            if st.button("Analisar Jogador"):
                profile = get_player_profile(match_id, player_id, include_analysis)
                if profile:
                    display_player_profile(profile)

if __name__ == "__main__":
    main()
