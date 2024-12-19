import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="Football Analysis App",
    page_icon="⚽",
    layout="wide"
)

class FootballDataClient:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
    
    def get_match_data(self, match_id: int):
        try:
            response = requests.get(f"{self.base_url}/matches/{match_id}")
            if response.status_code == 200:
                return response.json()
            st.error(f"Erro ao buscar dados: {response.status_code}")
            return None
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")
            return None
    
    def get_player_profile(self, match_id: int, player_id: int):
        try:
            response = requests.get(f"{self.base_url}/matches/{match_id}/player/{player_id}")
            if response.status_code == 200:
                return response.json()
            st.error(f"Erro ao buscar perfil: {response.status_code}")
            return None
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")
            return None
    
    def get_match_summary(self, match_id: int):
        try:
            response = requests.get(f"{self.base_url}/matches/{match_id}/summary")
            if response.status_code == 200:
                return response.json()
            st.error(f"Erro ao buscar resumo: {response.status_code}")
            return None
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")
            return None
    
    def get_match_narrative(self, match_id: int, style: str):
        try:
            response = requests.get(f"{self.base_url}/matches/{match_id}/narrative", params={"style": style})
            if response.status_code == 200:
                return response.json()
            st.error(f"Erro ao buscar narrativa: {response.status_code}")
            return None
        except Exception as e:
            st.error(f"Erro na requisição: {str(e)}")
            return None

class FootballAnalysisApp:
    def __init__(self):
        self.data_client = FootballDataClient()
    
    def show_match_overview(self, match_id: int):
        st.header("📊 Resumo da Partida")
        
        # Carregar dados
        match_data = self.data_client.get_match_data(match_id)
        if not match_data:
            return
        
        summary = self.data_client.get_match_summary(match_id)
        if not summary:
            return
        
        # Exibir eventos principais
        st.subheader("🎯 Eventos Principais")
        if 'events' in match_data:
            events_df = pd.DataFrame([
                {
                    'Minuto': event.get('minute', ''),
                    'Tipo': event.get('type', ''),
                    'Jogador': event.get('player', ''),
                    'Time': event.get('team', '')
                }
                for event in match_data['events']
                if event.get('type') in ['Goal', 'Card', 'Substitution']
            ])
            if not events_df.empty:
                st.dataframe(events_df, use_container_width=True)
        
        # Exibir estatísticas
        st.subheader("📈 Estatísticas")
        if 'statistics' in summary:
            stats_df = pd.DataFrame(summary['statistics'])
            fig = px.bar(stats_df, barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    def show_player_analysis(self, match_id: int, player_id: int):
        st.header("👤 Análise do Jogador")
        
        # Carregar dados do jogador
        player_data = self.data_client.get_player_profile(match_id, player_id)
        if not player_data:
            return
        
        # Informações básicas
        if 'info' in player_data:
            st.subheader(player_data['info'].get('player_name', 'Jogador'))
            st.write(f"Time: {player_data['info'].get('team', 'N/A')}")
        
        # Estatísticas
        if 'statistics' in player_data:
            st.subheader("📊 Estatísticas")
            stats = player_data['statistics']
            
            # Métricas principais
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Passes", stats.get('passes', {}).get('total', 0))
            with col2:
                st.metric("Finalizações", stats.get('shots', {}).get('total', 0))
            with col3:
                st.metric("Gols", stats.get('shots', {}).get('goals', 0))
            
            # Tabela completa
            st.dataframe(pd.DataFrame([stats]), use_container_width=True)
    
    def show_narrative(self, match_id: int):
        st.header("📝 Narrativa da Partida")
        
        # Seleção do estilo
        style = st.selectbox(
            "Estilo da Narrativa",
            ["formal", "humorous", "technical"]
        )
        
        if st.button("Gerar Narrativa"):
            narrative = self.data_client.get_match_narrative(match_id, style)
            if narrative:
                st.markdown(narrative)
    
    def main(self):
        st.title("⚽ Análise de Partidas de Futebol")
        
        # Sidebar para seleção
        with st.sidebar:
            st.header("⚙️ Configurações")
            match_id = st.number_input("ID da Partida", value=3788741)  # Turquia vs Itália
            
            analysis_type = st.radio(
                "Tipo de Análise",
                ["Visão Geral", "Análise de Jogador", "Narrativa"]
            )
        
        # Conteúdo principal
        if analysis_type == "Visão Geral":
            self.show_match_overview(match_id)
        
        elif analysis_type == "Análise de Jogador":
            player_id = st.number_input("ID do Jogador", value=11086)  # Burak Yilmaz
            self.show_player_analysis(match_id, player_id)
        
        else:  # Narrativa
            self.show_narrative(match_id)

if __name__ == "__main__":
    app = FootballAnalysisApp()
    app.main()
