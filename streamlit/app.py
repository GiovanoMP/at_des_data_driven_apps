import streamlit as st
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="Football Analysis App",
    page_icon="⚽",
    layout="wide"
)

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do modelo Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

class FootballDataClient:
    """Cliente para acessar dados de futebol da API"""
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.api_version = "v1"
        self.api_prefix = f"/api/{self.api_version}"
    
    def _get_url(self, endpoint: str) -> str:
        """Constrói a URL completa para a API"""
        return f"{self.base_url}{self.api_prefix}/{endpoint}"
    
    def get_competitions(self) -> List[Dict]:
        try:
            response = requests.get(self._get_url("competitions"))
            response.raise_for_status()
            return response.json()
        except Exception:
            st.info("Usando dados de exemplo para competições")
            return self._get_mock_competitions()
    
    def get_matches(self, competition_id: str, season: str) -> List[Dict]:
        try:
            response = requests.get(
                self._get_url(f"competitions/{competition_id}/seasons/{season}/matches")
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            st.info("Usando dados de exemplo para partidas")
            return self._get_mock_matches(competition_id, season)
    
    def get_match_details(self, match_id: str) -> Dict:
        try:
            response = requests.get(self._get_url(f"matches/{match_id}"))
            response.raise_for_status()
            return response.json()
        except Exception:
            st.info("Usando dados de exemplo para detalhes da partida")
            return self._get_mock_match_details(match_id)
    
    def _get_mock_competitions(self) -> List[Dict]:
        """Dados mockados para desenvolvimento"""
        return [
            {"id": "1", "name": "Premier League", "country": "Inglaterra", "seasons": ["2021/22", "2022/23"]},
            {"id": "2", "name": "La Liga", "country": "Espanha", "seasons": ["2021/22", "2022/23"]},
            {"id": "3", "name": "Serie A", "country": "Itália", "seasons": ["2021/22", "2022/23"]}
        ]
    
    def _get_mock_matches(self, competition_id: str, season: str) -> List[Dict]:
        return [
            {
                "id": "1", "competition_id": competition_id, "season": season,
                "home_team": "Manchester City", "away_team": "Liverpool",
                "date": "2024-03-10", "stadium": "Etihad Stadium"
            },
            {
                "id": "2", "competition_id": competition_id, "season": season,
                "home_team": "Arsenal", "away_team": "Chelsea",
                "date": "2024-03-09", "stadium": "Emirates Stadium"
            }
        ]
    
    def _get_mock_match_details(self, match_id: str) -> Dict:
        players = {
            "Manchester City": [
                {"name": "Haaland", "position": "FW", "number": 9},
                {"name": "De Bruyne", "position": "MF", "number": 17}
            ],
            "Liverpool": [
                {"name": "Salah", "position": "FW", "number": 11},
                {"name": "Van Dijk", "position": "DF", "number": 4}
            ]
        }
        
        events = [
            {"time": 23, "type": "Goal", "team": "Manchester City", "player": "Haaland"},
            {"time": 45, "type": "Goal", "team": "Liverpool", "player": "Salah"},
            {"time": 78, "type": "Goal", "team": "Manchester City", "player": "De Bruyne"},
            {"time": 65, "type": "Yellow Card", "team": "Liverpool", "player": "Van Dijk"}
        ]
        
        player_stats = {
            "Haaland": {
                "goals": 1, "shots": 4, "shots_on_target": 2, "passes": 15,
                "pass_accuracy": 80, "minutes_played": 90
            },
            "De Bruyne": {
                "goals": 1, "assists": 1, "passes": 45, "pass_accuracy": 89,
                "key_passes": 5, "minutes_played": 90
            }
        }
        
        return {
            "id": match_id,
            "home_team": "Manchester City",
            "away_team": "Liverpool",
            "home_score": 2,
            "away_score": 1,
            "date": "2024-03-10",
            "stadium": "Etihad Stadium",
            "referee": "Michael Oliver",
            "attendance": 53789,
            "players": players,
            "events": events,
            "player_stats": player_stats,
            "stats": {
                "possession": {"home": 55, "away": 45},
                "shots": {"home": 15, "away": 10},
                "shots_on_target": {"home": 8, "away": 4},
                "corners": {"home": 7, "away": 5},
                "fouls": {"home": 8, "away": 10}
            }
        }

class FootballAnalyzer:
    """Analisador de futebol usando Google Gemini"""
    
    def __init__(self, model):
        self.model = model
    
    def analyze_match(self, match_data: Dict) -> str:
        prompt = f"""
        Atue como um analista profissional de futebol e analise a seguinte partida:
        {json.dumps(match_data, indent=2)}
        
        Forneça:
        1. Um resumo geral da partida com o resultado final
        2. Análise dos momentos-chave, incluindo gols e chances importantes
        3. Avaliação tática de ambas as equipes
        4. Destaques individuais
        5. Análise das estatísticas principais
        
        Formate a resposta usando markdown para melhor legibilidade.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def analyze_player(self, player_data: Dict, style: str = "técnico") -> str:
        prompt = f"""
        Como especialista em análise de futebol, avalie o desempenho do seguinte jogador 
        em um estilo {style}:
        {json.dumps(player_data, indent=2)}
        
        Inclua:
        1. Resumo geral da atuação
        2. Análise das estatísticas principais
        3. Pontos fortes demonstrados
        4. Áreas para melhoria
        5. Impacto na partida
        
        Formate a resposta usando markdown.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_narrative(self, match_data: Dict, style: str) -> str:
        styles = {
            "formal": "profissional e objetiva, focando em fatos e análises técnicas",
            "humoristico": "descontraída e bem-humorada, usando analogias criativas",
            "tecnico": "detalhada e tática, focando em aspectos técnicos e estratégicos"
        }
        
        prompt = f"""
        Como narrador de futebol, crie uma narrativa {styles[style]} da seguinte partida:
        {json.dumps(match_data, indent=2)}
        
        Aborde:
        1. O desenvolvimento cronológico do jogo
        2. Os momentos decisivos
        3. As atuações individuais de destaque
        4. O contexto tático
        5. A atmosfera da partida
        
        Formate a resposta usando markdown.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def compare_players(self, player1_data: Dict, player2_data: Dict) -> str:
        prompt = f"""
        Compare o desempenho dos seguintes jogadores:
        
        Jogador 1:
        {json.dumps(player1_data, indent=2)}
        
        Jogador 2:
        {json.dumps(player2_data, indent=2)}
        
        Forneça:
        1. Comparação estatística direta
        2. Análise dos pontos fortes de cada um
        3. Impacto no jogo
        4. Conclusão sobre quem teve melhor desempenho
        
        Formate a resposta usando markdown.
        """
        
        response = self.model.generate_content(prompt)
        return response.text

class FootballAnalysisApp:
    def __init__(self):
        self.data_client = FootballDataClient()
        self.analyzer = FootballAnalyzer(model)
        
        # Inicializar estado da sessão
        for key in ['competition', 'season', 'match']:
            if f'selected_{key}' not in st.session_state:
                st.session_state[f'selected_{key}'] = None
    
    def main(self):
        st.title("⚽ Análise de Partidas de Futebol")
        
        # Sidebar para seleção
        with st.sidebar:
            st.title("Configurações")
            self.show_match_selector()
        
        if st.session_state.selected_match:
            tabs = st.tabs([
                "Visão Geral",
                "Análise de Jogadores",
                "Análise Narrativa",
                "Comparação"
            ])
            
            with tabs[0]:
                self.show_match_overview()
            with tabs[1]:
                self.show_players_analysis()
            with tabs[2]:
                self.show_narrative_analysis()
            with tabs[3]:
                self.show_comparison_analysis()
        else:
            st.info("👈 Selecione uma partida no menu lateral para começar")
    
    def show_match_selector(self):
        """Interface de seleção de partida"""
        competitions = self.data_client.get_competitions()
        
        competition = st.selectbox(
            "Competição",
            options=competitions,
            format_func=lambda x: f"{x['name']} ({x['country']})",
            key="competition_selector"
        )
        
        if competition:
            st.session_state.selected_competition = competition
            season = st.selectbox(
                "Temporada",
                options=competition.get('seasons', []),  # Certifique-se de que a API retorna as temporadas
                key="season_selector"
            )
            
            if season:
                st.session_state.selected_season = season
                matches = self.data_client.get_matches(competition['id'], season)
                
                match = st.selectbox(
                    "Partida",
                    options=matches,
                    format_func=lambda x: (
                        f"{x['home_team']} vs {x['away_team']} "
                        f"({x['date']})"
                    ),
                    key="match_selector"
                )
                
                if match:
                    st.session_state.selected_match = match
    
    def show_match_overview(self):
        """Página de visão geral da partida"""
        st.header("Visão Geral da Partida")
        
        match_data = self.data_client.get_match_details(
            st.session_state.selected_match['id']
        )
        
        # Placar e informações básicas
        col1, col2, col3 = st.columns([2,1,2])
        with col1:
            st.metric(
                "Time Casa",
                match_data['home_team'],
                match_data['home_score']
            )
        with col2:
            st.metric("Estádio", match_data['stadium'])
        with col3:
            st.metric(
                "Time Visitante",
                match_data['away_team'],
                match_data['away_score']
            )
        
        # Análise geral
        with st.expander("Análise da Partida", expanded=True):
            with st.spinner("Gerando análise..."):
                analysis = self.analyzer.analyze_match(match_data)
                st.markdown(analysis)
        
        # Estatísticas
        self.show_match_stats(match_data.get('stats', {}))
        
        # Eventos
        self.show_match_events(match_data.get('events', []))
    
    def show_players_analysis(self):
        """Página de análise de jogadores"""
        st.header("Análise de Jogadores")
        
        match_data = self.data_client.get_match_details(
            st.session_state.selected_match['id']
        )
        
        # Lista de jogadores
        all_players = []
        for team, players in match_data.get('players', {}).items():
            for player in players:
                all_players.append(f"{player['name']} ({team})")
        
        player_name = st.selectbox(
            "Selecione um jogador",
            options=all_players
        )
        
        if player_name:
            player_data = self._get_player_data(match_data, player_name)
            if player_data:
                style = st.radio(
                    "Estilo de análise",
                    ["técnico", "formal", "humoristico"]
                )
                
                with st.spinner("Analisando jogador..."):
                    analysis = self.analyzer.analyze_player(player_data, style)
                    st.markdown(analysis)
                
                if 'stats' in player_data:
                    self.show_player_stats(player_data['stats'])
    
    def show_narrative_analysis(self):
        """Página de análise narrativa"""
        st.header("Análise Narrativa")
        
        style = st.selectbox(
            "Estilo de Narrativa",
            options=["formal", "humoristico", "tecnico"],
            format_func=lambda x: x.capitalize()
        )
        
        if st.button("Gerar Narrativa"):
            match_data = self.data_client.get_match_details(
                st.session_state.selected_match['id']
            )
            
            with st.spinner("Gerando narrativa..."):
                narrative = self.analyzer.generate_narrative(match_data, style)
                st.markdown(narrative)  

    def show_comparison_analysis(self):
        """Página de comparação entre jogadores"""
        st.header("Comparação entre Jogadores")
        
        match_data = self.data_client.get_match_details(
            st.session_state.selected_match['id']
        )
        
        # Lista de jogadores para seleção
        all_players = []
        for team, players in match_data.get('players', {}).items():
            for player in players:
                all_players.append(f"{player['name']} ({team})")
        
        col1, col2 = st.columns(2)
        
        with col1:
            player1 = st.selectbox(
                "Primeiro Jogador",
                options=all_players,
                key="player1"
            )
        
        with col2:
            player2 = st.selectbox(
                "Segundo Jogador",
                options=all_players,
                key="player2"
            )
        
        if player1 and player2 and player1 != player2:
            player1_data = self._get_player_data(match_data, player1)
            player2_data = self._get_player_data(match_data, player2)
            
            if player1_data and player2_data:
                with st.spinner("Gerando comparação..."):
                    comparison = self.analyzer.compare_players(player1_data, player2_data)
                    st.markdown(comparison)
                    
                    # Visualização das estatísticas
                    self.show_player_comparison_stats(player1_data, player2_data)

    def show_player_stats(self, stats: Dict):
        """Exibe estatísticas do jogador em formato visual"""
        if stats:
            # Criar gráfico de barras para estatísticas principais
            fig = px.bar(
                x=list(stats.keys()),
                y=list(stats.values()),
                title="Estatísticas do Jogador"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela detalhada
            st.dataframe(pd.DataFrame([stats]))

    def show_player_comparison_stats(self, player1: Dict, player2: Dict):
        """Exibe comparação visual entre dois jogadores"""
        stats1 = player1.get('stats', {})
        stats2 = player2.get('stats', {})
        
        # Criar DataFrame para comparação
        df = pd.DataFrame({
            'Estatística': list(stats1.keys()),
            player1['name']: list(stats1.values()),
            player2['name']: list(stats2.values())
        })
        
        # Gráfico de comparação
        fig = px.bar(
            df,
            x='Estatística',
            y=[player1['name'], player2['name']],
            barmode='group',
            title=f"Comparação: {player1['name']} vs {player2['name']}"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.dataframe(df.set_index('Estatística'))

if __name__ == "__main__":
    app = FootballAnalysisApp()
    app.main()