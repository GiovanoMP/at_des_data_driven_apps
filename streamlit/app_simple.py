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

# Configuração OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_match_data() -> Optional[Dict]:
    """Obtém dados da partida"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter dados: {str(e)}")
        return None

def get_match_summary() -> Optional[Dict]:
    """Obtém resumo da partida"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/summary")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter resumo: {str(e)}")
        return None

def get_player_profile(player_id: float) -> Optional[Dict]:
    """Obtém perfil do jogador"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/player/{player_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter perfil: {str(e)}")
        return None

def get_match_analysis(style: str) -> Optional[Dict]:
    """Obtém análise narrativa"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/analysis?style={style}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter análise: {str(e)}")
        return None

def generate_match_summary(match_data: Dict, summary_data: Dict) -> str:
    """Gera um resumo da partida usando LLM"""
    try:
        # Contexto do jogo
        match_context = f"""
        Partida: {match_data['home_team']} vs {match_data['away_team']}
        Placar: {match_data['score']}
        Data: {match_data['date']}
        
        Gols ({len(summary_data['goals'])}):
        {[f"⚽ {goal['minute']}' - {goal['scorer']} ({goal['team']})" for goal in summary_data['goals']]}
        
        Cartões ({len(summary_data['cards'])}):
        {[f"🟨 {card['minute']}' - {card['player']} ({card['team']})" for card in summary_data['cards']]}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """Você é um especialista em análise de futebol.
                 Gere um resumo conciso mas informativo da partida, destacando:
                 1. O placar e resultado geral
                 2. Os momentos-chave do jogo (gols e cartões)
                 3. Uma breve análise do desenrolar da partida"""},
                {"role": "user", "content": f"Gere um resumo da seguinte partida:\n{match_context}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar resumo: {str(e)}")
        return None

def show_match_info(match_data: Dict):
    """Mostra informações da partida"""
    col1, col2, col3 = st.columns([2,3,2])
    with col1:
        st.subheader(match_data['home_team'])
    with col2:
        st.title(match_data['score'])
        st.caption(f"Data: {match_data['date']}")
    with col3:
        st.subheader(match_data['away_team'])

def show_events_timeline(events: List[Dict]):
    """Mostra timeline de eventos"""
    fig = go.Figure()
    
    for event in events:
        fig.add_trace(go.Scatter(
            x=[event['minute']],
            y=[event['team']],
            mode='markers+text',
            name=event['type'],
            text=[f"{event['type']} - {event.get('scorer', event.get('player', 'N/A'))}"],
            marker=dict(
                size=15,
                symbol='circle' if event['type'] == 'Goal' else 'square'
            )
        ))
    
    fig.update_layout(
        title="Timeline de Eventos",
        xaxis_title="Minuto",
        yaxis_title="Time",
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_player_stats(player_data: Dict):
    """Mostra estatísticas do jogador"""
    info = player_data['info']
    stats = player_data['statistics']
    
    st.subheader(f"📊 Estatísticas de {info['player_name']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Passes Totais", stats['passes']['total'])
        st.metric("Finalizações", stats['shots']['total'])
    with col2:
        st.metric("Passes Completos", stats['passes']['successful'])
        st.metric("Gols", stats['shots']['goals'])

def show_chat_interface(match_data: Dict):
    """Interface de chat para perguntas sobre a partida"""
    st.subheader("💬 Chat sobre a Partida")
    
    # Inicializar histórico do chat
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Mostrar histórico
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Input do usuário
    if prompt := st.chat_input("Faça uma pergunta sobre a partida..."):
        # Adicionar mensagem do usuário
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Contexto do jogo para o LLM
        match_context = f"""
        Partida: {match_data['home_team']} vs {match_data['away_team']}
        Placar: {match_data['score']}
        Data: {match_data['date']}
        
        Eventos principais:
        {[f"{event['minute']}' - {event['type']} - {event.get('scorer', event.get('player', 'N/A'))} ({event['team']})" for event in match_data['events']]}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """Você é um especialista em futebol.
                     Responda perguntas sobre a partida de forma clara e precisa.
                     Use os dados fornecidos para embasar suas respostas.
                     Se não tiver certeza sobre algo, admita que não tem a informação."""},
                    {"role": "user", "content": f"Com base nos seguintes dados da partida:\n{match_context}\n\nPergunta: {prompt}"}
                ],
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.write(assistant_response)
        
        except Exception as e:
            st.error(f"Erro ao gerar resposta: {str(e)}")

def main():
    st.title("⚽ Análise de Partida de Futebol")
    
    # Carregar dados da partida
    match_data = get_match_data()
    if not match_data:
        st.error("Não foi possível carregar os dados da partida")
        return
    
    # Layout em duas colunas principais
    col_main, col_chat = st.columns([2, 1])
    
    with col_main:
        # Mostrar informações básicas
        show_match_info(match_data)
        
        # Tabs para diferentes seções
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Eventos",
            "📝 Resumo",
            "👤 Jogadores",
            "📖 Narrativas"
        ])
        
        with tab1:
            st.header("📊 Eventos da Partida")
            summary = get_match_summary()
            if summary:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total de Gols", len(summary['goals']))
                with col2:
                    st.metric("Total de Cartões", len(summary['cards']))
            
            show_events_timeline(match_data['events'])
        
        with tab2:
            st.header("📝 Resumo da Partida")
            summary = get_match_summary()
            if summary:
                with st.spinner("Gerando resumo..."):
                    match_summary = generate_match_summary(match_data, summary)
                    if match_summary:
                        st.markdown(match_summary)
        
        with tab3:
            st.header("👤 Análise de Jogadores")
            player_id = st.number_input("ID do Jogador", value=11086.0, step=0.1)
            if st.button("Analisar Jogador"):
                player_data = get_player_profile(player_id)
                if player_data:
                    show_player_stats(player_data)
        
        with tab4:
            st.header("📖 Narrativas da Partida")
            style = st.selectbox(
                "Escolha o estilo da narrativa",
                ["formal", "humoristico", "tecnico"],
                help="Formal: análise objetiva\nHumorístico: tom descontraído\nTécnico: foco em estatísticas"
            )
            
            if st.button("Gerar Narrativa"):
                with st.spinner("Gerando narrativa..."):
                    analysis = get_match_analysis(style)
                    if analysis and 'analysis' in analysis:
                        st.markdown(analysis['analysis'])
    
    # Chat em coluna separada
    with col_chat:
        show_chat_interface(match_data)

if __name__ == "__main__":
    main()
