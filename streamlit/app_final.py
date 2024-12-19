import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI

# Configuração inicial
load_dotenv()
st.set_page_config(
    page_title="⚽ Football Analysis Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações
API_BASE_URL = "http://localhost:8000/api/v1"
MATCH_ID = 3788741  # Turquia vs Itália

# Configuração OpenAI para o chat
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class FootballAnalysisApp:
    def __init__(self):
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'match_data' not in st.session_state:
            st.session_state.match_data = self.get_match_data()
            
    def get_match_data(self) -> Optional[Dict]:
        """Obtém dados da partida da API"""
        try:
            response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter dados da partida: {str(e)}")
            return None

    def get_player_profile(self, player_id: float) -> Optional[Dict]:
        """Obtém perfil do jogador da API"""
        try:
            response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/player/{player_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter perfil do jogador: {str(e)}")
            return None

    def get_match_summary(self) -> Optional[Dict]:
        """Obtém resumo da partida da API"""
        try:
            response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/summary")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter resumo da partida: {str(e)}")
            return None

    def get_match_analysis(self, style: str = "formal") -> Optional[Dict]:
        """Obtém análise narrativa da API"""
        try:
            response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/analysis?style={style}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter análise da partida: {str(e)}")
            return None

    def show_match_header(self, match_data: Dict):
        """Mostra cabeçalho com informações básicas da partida"""
        col1, col2, col3 = st.columns([2,3,2])
        
        with col1:
            st.subheader(match_data['home_team'])
        with col2:
            st.title(match_data['score'])
            st.caption(f"Data: {match_data['date']}")
        with col3:
            st.subheader(match_data['away_team'])

    def show_events_timeline(self, events: List[Dict]):
        """Mostra linha do tempo de eventos"""
        st.subheader("📊 Timeline de Eventos")
        
        # Criar figura do Plotly
        fig = go.Figure()
        
        # Adicionar eventos
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
            title="Eventos da Partida",
            xaxis_title="Minuto",
            yaxis_title="Time",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def show_player_analysis(self, player_data: Dict):
        """Mostra análise detalhada do jogador"""
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
        
        if 'analysis' in player_data:
            st.markdown("### 📝 Análise")
            st.markdown(player_data['analysis'])

    def show_chat_interface(self):
        """Interface de chat para perguntas sobre a partida"""
        st.subheader("💬 Pergunte sobre a Partida")
        
        # Mostrar mensagens anteriores
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input do usuário
        if prompt := st.chat_input("Faça uma pergunta sobre a partida..."):
            # Adicionar mensagem do usuário
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Gerar resposta
            match_context = f"""
            Partida: {st.session_state.match_data['home_team']} vs {st.session_state.match_data['away_team']}
            Placar: {st.session_state.match_data['score']}
            Data: {st.session_state.match_data['date']}
            """
            
            full_prompt = f"""Com base nos seguintes dados da partida:
            {match_context}
            
            Responda à seguinte pergunta: {prompt}
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Você é um especialista em análise de futebol."},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7
                )
                
                # Adicionar resposta do assistente
                assistant_response = response.choices[0].message.content
                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
            
            except Exception as e:
                st.error(f"Erro ao gerar resposta: {str(e)}")

    def main(self):
        """Função principal da aplicação"""
        st.title("⚽ Análise de Partida de Futebol")
        
        if st.session_state.match_data:
            self.show_match_header(st.session_state.match_data)
            
            # Tabs para diferentes visualizações
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Eventos",
                "👤 Análise de Jogadores",
                "📝 Narrativas",
                "💬 Chat"
            ])
            
            with tab1:
                # Mostrar eventos
                summary = self.get_match_summary()
                if summary:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total de Gols", len(summary['goals']))
                    with col2:
                        st.metric("Total de Cartões", len(summary['cards']))
                
                self.show_events_timeline(st.session_state.match_data['events'])
            
            with tab2:
                # Análise de jogadores
                st.subheader("Análise de Jogadores")
                player_id = st.number_input("ID do Jogador", value=11086.0, step=0.1)
                
                if st.button("Analisar Jogador"):
                    player_data = self.get_player_profile(player_id)
                    if player_data:
                        self.show_player_analysis(player_data)
            
            with tab3:
                # Narrativas
                st.subheader("Narrativas da Partida")
                style = st.selectbox("Estilo de Narrativa", ["formal", "humoristico", "tecnico"])
                
                if st.button("Gerar Narrativa"):
                    analysis = self.get_match_analysis(style)
                    if analysis and 'analysis' in analysis:
                        st.markdown(analysis['narrative'])
            
            with tab4:
                # Interface de chat
                self.show_chat_interface()

if __name__ == "__main__":
    app = FootballAnalysisApp()
    app.main()
