import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Configuração inicial
load_dotenv()
st.set_page_config(
    page_title="⚽ Football Analysis Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração da API OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Constantes
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_MATCH_ID = 3788741  # Turquia vs Itália
STYLES = ["formal", "humoristico", "tecnico"]

class FootballAnalysisAPI:
    """Cliente para acessar a API de análise de futebol"""
    
    @staticmethod
    def get_competitions() -> List[Dict]:
        """Obtém lista de competições disponíveis"""
        try:
            response = requests.get(f"{API_BASE_URL}/competitions")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter competições: {str(e)}")
            return []

    @staticmethod
    def get_matches(competition_id: str, season: str) -> List[Dict]:
        """Obtém lista de partidas de uma competição/temporada"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/competitions/{competition_id}/seasons/{season}/matches"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter partidas: {str(e)}")
            return []
    
    @staticmethod
    def get_match_data(match_id: int) -> Optional[Dict]:
        """Obtém os dados de uma partida específica"""
        try:
            response = requests.get(f"{API_BASE_URL}/matches/{match_id}")
            response.raise_for_status()
            data = response.json()
            
            # Processar o score (formato "2-1")
            home_score, away_score = data['score'].split('-')
            
            match_info = {
                'match_id': data['match_id'],
                'home_team': data['home_team'],
                'away_team': data['away_team'],
                'home_score': int(home_score),
                'away_score': int(away_score),
                'date': data['date'],
                'stadium': data['stadium'],
                'events': []
            }
            
            # Processar eventos
            if 'events' in data and isinstance(data['events'], list):
                match_info['events'] = [
                    {
                        'id': event['id'],
                        'type': event['type'],
                        'minute': event['minute'],
                        'team': event['team'],
                        'player': event['player'],
                        'assist': event.get('assist', None),
                        'card_type': event.get('card_type', None)
                    }
                    for event in data['events']
                ]
            
            return match_info
            
        except Exception as e:
            st.error(f"Erro ao obter dados da partida: {str(e)}")
            return None

    @staticmethod
    def get_match_summary(match_id: int) -> Optional[Dict]:
        """Obtém o resumo de uma partida"""
        try:
            response = requests.get(f"{API_BASE_URL}/matches/{match_id}/summary")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter resumo da partida: {str(e)}")
            return None
    
    @staticmethod
    def get_player_profile(match_id: int, player_id: float, include_analysis: bool = False) -> Optional[Dict]:
        """Obtém o perfil de um jogador"""
        try:
            url = f"{API_BASE_URL}/matches/{match_id}/player/{player_id}"
            if include_analysis:
                url += "?include_analysis=true"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter perfil do jogador: {str(e)}")
            return None
    
    @staticmethod
    def get_match_analysis(match_id: int, style: str = "formal") -> Optional[Dict]:
        """Obtém a análise narrativa de uma partida"""
        try:
            response = requests.get(f"{API_BASE_URL}/matches/{match_id}/analysis?style={style}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao obter análise da partida: {str(e)}")
            return None

class FootballChatbot:
    """Chatbot especializado em análise de futebol usando OpenAI"""
    
    def __init__(self):
        self.messages = []
        self.setup_system_prompt()
    
    def setup_system_prompt(self):
        """Configura o prompt inicial do sistema"""
        self.messages = [{
            "role": "system",
            "content": """Você é um analista profissional de futebol especializado em:
            1. Análise tática de partidas
            2. Avaliação de desempenho de jogadores
            3. Interpretação de estatísticas
            4. Explicação de eventos do jogo
            
            Responda sempre de forma clara e objetiva, usando seu conhecimento técnico
            quando apropriado, mas mantendo a linguagem acessível.
            
            Quando relevante, você pode sugerir análises adicionais ou pedir mais
            informações para fornecer uma resposta mais completa."""
        }]
    
    def add_context(self, match_data: Dict):
        """Adiciona contexto da partida ao chat"""
        context = {
            "role": "system",
            "content": f"""Contexto da partida atual:
            {json.dumps(match_data, indent=2)}
            
            Use estas informações para responder às perguntas do usuário."""
        }
        self.messages.append(context)
    
    def chat(self, user_input: str) -> str:
        """Processa a entrada do usuário e retorna uma resposta"""
        self.messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=self.messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        
        except Exception as e:
            st.error(f"Erro ao processar mensagem: {str(e)}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem."

class FootballAnalysisApp:
    """Aplicativo principal de análise de futebol"""
    
    def __init__(self):
        self.api = FootballAnalysisAPI()
        self.chatbot = FootballChatbot()
        
        # Inicializar estado da sessão
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'selected_match' not in st.session_state:
            st.session_state.selected_match = None
        if 'matches' not in st.session_state:
            st.session_state.matches = []
    
    def show_match_selector(self):
        """Interface de seleção de partida"""
        st.sidebar.header("⚙️ Seleção de Partida")
        
        # Obter competições
        competitions = self.api.get_competitions()
        
        if competitions:
            # Seleção de competição
            competition = st.sidebar.selectbox(
                "Competição",
                options=competitions,
                format_func=lambda x: f"{x['name']} ({x['country']})"
            )
            
            if competition:
                # Seleção de temporada
                season = st.sidebar.selectbox(
                    "Temporada",
                    options=competition['seasons']
                )
                
                if season:
                    # Carregar partidas se necessário
                    if st.sidebar.button("🔄 Carregar Partidas"):
                        matches = self.api.get_matches(competition['id'], season)
                        if matches:
                            st.session_state.matches = matches
                            st.sidebar.success(f"Carregadas {len(matches)} partidas!")
                    
                    # Seleção de partida
                    if st.session_state.matches:
                        match = st.sidebar.selectbox(
                            "Partida",
                            options=st.session_state.matches,
                            format_func=lambda x: (
                                f"{x['home_team']} vs {x['away_team']} "
                                f"({x['date']})"
                            )
                        )
                        
                        if match:
                            if st.sidebar.button("📊 Analisar Partida"):
                                match_data = self.api.get_match_data(match['match_id'])
                                if match_data:
                                    st.session_state.selected_match = match_data
                                    self.chatbot.add_context(match_data)
    
    def show_match_header(self, match_data: Dict):
        """Exibe o cabeçalho com informações da partida"""
        st.header("🏟️ Informações da Partida")
        
        col1, col2, col3 = st.columns([2,1,2])
        with col1:
            st.metric(
                match_data['home_team'],
                match_data['home_score']
            )
        with col2:
            st.markdown(f"### {match_data['stadium']}")
        with col3:
            st.metric(
                match_data['away_team'],
                match_data['away_score']
            )
        
        st.markdown(f"""
        **🗓️ Data:** {match_data['date']}  
        **🏟️ Estádio:** {match_data['stadium']}
        """)
    
    def show_match_events(self, events: List[Dict]):
        """Exibe os eventos da partida"""
        if not events:
            st.warning("Nenhum evento registrado para esta partida.")
            return
        
        st.subheader("📊 Eventos da Partida")
        
        # Separar eventos por tipo
        goals = [e for e in events if e['type'] == 'Goal']
        cards = [e for e in events if e['type'] == 'Card']
        
        # Mostrar gols
        if goals:
            st.markdown("### ⚽ Gols")
            for goal in goals:
                st.markdown(
                    f"**{goal['minute']}'** - {goal['player']} ({goal['team']}) "
                    f"{f'Assist: {goal['assist']}' if goal.get('assist') else ''}"
                )
        
        # Mostrar cartões
        if cards:
            st.markdown("### 🟨 Cartões")
            for card in cards:
                emoji = "🟨" if card.get('card_type') == "Yellow" else "🟥"
                st.markdown(
                    f"**{card['minute']}'** {emoji} - {card['player']} ({card['team']})"
                )
        
        # Timeline visual
        fig = go.Figure()
        
        # Adicionar eventos na timeline
        for event in events:
            fig.add_trace(go.Scatter(
                x=[event['minute']],
                y=[event['team']],
                mode='markers+text',
                name=event['type'],
                text=[f"{event['type']}: {event['player']}"],
                marker=dict(
                    size=15,
                    symbol='circle' if event['type'] == 'Goal' else 'square'
                )
            ))
        
        fig.update_layout(
            title="Timeline da Partida",
            xaxis_title="Minuto",
            yaxis_title="Time",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def show_player_stats(self, player_data: Dict):
        """Exibe estatísticas do jogador em formato visual"""
        st.subheader(f"📈 Estatísticas de {player_data['info']['player_name']}")
        
        stats = player_data['statistics']
        
        # Criar visualizações para diferentes tipos de estatísticas
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de passes
            fig_passes = go.Figure()
            fig_passes.add_trace(go.Bar(
                x=['Total', 'Bem sucedidos'],
                y=[stats['passes']['total'], stats['passes']['successful']],
                name='Passes'
            ))
            fig_passes.update_layout(title="Estatísticas de Passes")
            st.plotly_chart(fig_passes, use_container_width=True)
        
        with col2:
            # Gráfico de outras estatísticas
            fig_other = go.Figure()
            fig_other.add_trace(go.Bar(
                x=['Finalizações', 'Desarmes', 'Interceptações'],
                y=[stats['shots']['total'], stats['tackles'], stats['interceptions']],
                name='Outras Estatísticas'
            ))
            fig_other.update_layout(title="Outras Estatísticas")
            st.plotly_chart(fig_other, use_container_width=True)
    
    def show_chat_interface(self, chat_prompt: str):
        """Exibe a interface do chat"""
        st.subheader("💬 Chat com Analista")
        
        # Exibir mensagens anteriores
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Processar nova mensagem
        if chat_prompt:
            st.session_state.chat_messages.append({"role": "user", "content": chat_prompt})
            with st.chat_message("user"):
                st.markdown(chat_prompt)
            
            with st.chat_message("assistant"):
                response = self.chatbot.chat(chat_prompt)
                st.markdown(response)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    def main(self):
        """Função principal do aplicativo"""
        st.title("⚽ Football Analysis Hub")
        
        self.show_match_selector()
        
        # Chat input (fora das tabs)
        chat_prompt = st.chat_input("Faça uma pergunta sobre a partida...")
        
        # Conteúdo principal
        if st.session_state.selected_match:
            # Tabs para diferentes visualizações
            tab1, tab2, tab3 = st.tabs([
                "📊 Visão Geral",
                "👤 Análise de Jogadores",
                "📝 Narrativas"
            ])
            
            with tab1:
                self.show_match_header(st.session_state.selected_match)
                self.show_match_events(st.session_state.selected_match['events'])
                
                # Exibir sumário
                summary = self.api.get_match_summary(st.session_state.selected_match['match_id'])
                if summary:
                    st.subheader("📋 Resumo da Partida")
                    st.write(f"**Gols:** {len(summary.get('goals', []))}")
                    st.write(f"**Cartões:** {len(summary.get('cards', []))}")
            
            with tab2:
                st.subheader("👥 Análise de Jogadores")
                player_id = st.number_input("ID do Jogador", value=11086.0)
                include_analysis = st.checkbox("Incluir análise detalhada")
                
                if st.button("Analisar Jogador"):
                    player_data = self.api.get_player_profile(st.session_state.selected_match['match_id'], player_id, include_analysis)
                    if player_data:
                        self.show_player_stats(player_data)
                        if include_analysis and 'analysis' in player_data:
                            st.markdown(player_data['analysis'])
            
            with tab3:
                st.subheader("📖 Narrativas da Partida")
                style = st.selectbox("Estilo de Narrativa", STYLES)
                
                if st.button("Gerar Narrativa"):
                    analysis = self.api.get_match_analysis(st.session_state.selected_match['match_id'], style)
                    if analysis and 'analysis' in analysis:
                        st.markdown(analysis['analysis'].get('narrative', ''))
            
            # Chat interface (fora das tabs)
            st.markdown("---")
            self.show_chat_interface(chat_prompt)
        
        else:
            st.info("👈 Selecione uma partida no menu lateral para começar")

if __name__ == "__main__":
    app = FootballAnalysisApp()
    app.main()
