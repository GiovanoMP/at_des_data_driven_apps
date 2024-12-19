import streamlit as st
import requests
import plotly.graph_objects as go
from typing import Dict, List
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Configuração
load_dotenv()
st.set_page_config(layout="wide", page_title="⚽ Análise de Futebol")

# APIs e Configurações
API_BASE_URL = "http://localhost:8000/api/v1"
MATCH_ID = 3788741  # Turquia vs Itália
PLAYER_ID = 11086.0  # Burak Yilmaz

# Cliente OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Estado do chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

def get_match_data() -> Dict:
    """Função genérica para chamadas à API"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro na API: {str(e)}")
        return {}

def get_match_summary() -> Dict:
    """Obtém resumo da partida via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/summary")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter resumo: {str(e)}")
        return {}

def get_player_profile(include_analysis: bool = True) -> Dict:
    """Obtém perfil do jogador via API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/matches/{MATCH_ID}/player/{PLAYER_ID}",
            params={"include_analysis": include_analysis}
        )
        response.raise_for_status()
        data = response.json()
        
        # Adiciona análise se solicitado
        if include_analysis:
            analysis_response = requests.get(
                f"{API_BASE_URL}/matches/{MATCH_ID}/player/{PLAYER_ID}/analysis"
            )
            if analysis_response.ok:
                data['analysis'] = analysis_response.json().get('analysis', '')
        
        return data
    except Exception as e:
        st.error(f"Erro ao obter perfil: {str(e)}")
        return {}

def get_match_analysis(style: str) -> str:
    """Obtém análise da partida via API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/matches/{MATCH_ID}/analysis",
            params={"style": style}
        )
        response.raise_for_status()
        data = response.json()
        return data.get('narrative', '')  # Agora usando o campo correto
    except Exception as e:
        st.error(f"Erro ao obter análise: {str(e)}")
        return ""

def generate_llm_summary(match_data: Dict) -> str:
    """Gera um resumo personalizado usando GPT-4"""
    try:
        events_text = "\n".join([
            f"{event['minute']}' - {event['type']} - {event['player']} ({event['team']})"
            for event in match_data['events']
        ])
        
        prompt = f"""
        Você é um especialista em análise de futebol. Analise esta partida:
        
        {match_data['home_team']} vs {match_data['away_team']}
        Placar: {match_data['score']}
        Data: {match_data['date']}
        Estádio: {match_data['stadium']}
        
        Eventos:
        {events_text}
        
        Forneça:
        1. Análise tática
        2. Momentos-chave
        3. Destaques individuais
        4. Conclusão
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um analista de futebol profissional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar resumo com LLM: {str(e)}")
        return "Não foi possível gerar o resumo."

def create_timeline(events: List[Dict]) -> go.Figure:
    """Cria timeline de eventos"""
    fig = go.Figure()
    
    for event in events:
        emoji = "⚽" if event['type'] == "Goal" else "🟨"
        fig.add_trace(go.Scatter(
            x=[event['minute']],
            y=[event['team']],
            mode='markers+text',
            name=event['type'],
            text=[f"{emoji} {event['minute']}' - {event['player']}"],
            marker=dict(
                size=20,
                symbol='circle' if event['type'] == 'Goal' else 'square',
                color='blue' if event['team'] == 'Italy' else 'red'
            )
        ))
    
    fig.update_layout(
        title="Timeline da Partida",
        xaxis_title="Minuto",
        yaxis_title="Time",
        height=400
    )
    
    return fig

def chat_with_context(prompt: str, match_data: Dict) -> str:
    """Chat com contexto usando OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de futebol."},
                {"role": "user", "content": f"Dados da partida:\n{json.dumps(match_data, indent=2)}\n\nPergunta: {prompt}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

def main():
    st.title("⚽ Análise de Futebol")
    
    # Carrega dados da partida
    match_data = get_match_data()
    if not match_data:
        st.error("Não foi possível carregar os dados da partida")
        return
    
    # Cabeçalho da partida
    col1, col2, col3 = st.columns([2,3,2])
    with col1:
        st.subheader(f"🇹🇷 {match_data['home_team']}")
    with col2:
        st.title(match_data['score'])
        st.caption(f"Data: {match_data['date']}")
        st.caption(f"Local: {match_data['stadium']}")
    with col3:
        st.subheader(f"🇮🇹 {match_data['away_team']}")
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Eventos",
        "📝 Resumo",
        "👤 Jogador",
        "🎯 Narrativas"
    ])
    
    # Tab 1: Eventos
    with tab1:
        st.plotly_chart(create_timeline(match_data['events']), use_container_width=True)
        
        st.subheader("📝 Detalhes dos Eventos")
        for event in match_data['events']:
            emoji = "⚽" if event['type'] == "Goal" else "🟨"
            details = []
            if event.get('assist'):
                details.append(f"Assistência: {event['assist']}")
            if event.get('description'):
                details.append(event['description'])
            
            detail_text = f" ({', '.join(details)})" if details else ""
            st.write(f"{emoji} {event['minute']}' - {event['player']} ({event['team']}){detail_text}")
    
    # Tab 2: Resumo
    with tab2:
        with st.spinner("Gerando resumo detalhado..."):
            summary = generate_llm_summary(match_data)
            if summary:
                st.markdown(summary)
    
    # Tab 3: Jogador
    with tab3:
        player = get_player_profile(include_analysis=True)
        if player and 'info' in player and 'statistics' in player:
            st.subheader(f"👤 {player['info']['player_name']}")
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            stats = player['statistics']
            
            with col1:
                st.metric("Passes", f"{stats['passes']['successful']}/{stats['passes']['total']}")
                st.caption(f"Precisão: {stats['passes']['accuracy']}%")
            
            with col2:
                st.metric("Finalizações", f"{stats['shots']['on_target']}/{stats['shots']['total']}")
                st.caption(f"Gols: {stats['shots']['goals']}")
            
            with col3:
                st.metric("Desarmes", f"{stats['tackles']['successful']}/{stats['tackles']['total']}")
            
            if 'analysis' in player:
                st.markdown("### 📊 Análise Detalhada")
                st.markdown(player['analysis'])
    
    # Tab 4: Narrativas
    with tab4:
        style = st.selectbox(
            "Estilo de Narrativa",
            ["formal", "humoristico", "tecnico"],
            format_func=lambda x: {
                "formal": "🎯 Formal - Análise objetiva",
                "humoristico": "😄 Humorístico - Tom descontraído",
                "tecnico": "📊 Técnico - Foco em estatísticas"
            }[x]
        )
        
        if st.button("Gerar Narrativa"):
            with st.spinner("Gerando narrativa..."):
                narrative = get_match_analysis(style)
                if narrative:
                    st.markdown(narrative)
    
    # Chat (fora das colunas)
    st.markdown("---")
    st.header("💬 Chat sobre a Partida")
    
    # Histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Input
    if prompt := st.chat_input("Pergunte sobre a partida..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Resposta
        response = chat_with_context(prompt, match_data)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

if __name__ == "__main__":
    main()