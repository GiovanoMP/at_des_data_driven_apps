# Core imports
import streamlit as st
from typing import Dict, List, Any
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import plotly.express as px
import json

# LangChain imports
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.agents.react.base import ReActDocstoreAgent
from langchain_google_genai import ChatGoogleGenerativeAI  # Correção aqui
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# Configuração inicial do Streamlit
st.set_page_config(
    page_title="Football Analysis App",
    page_icon="⚽",
    layout="wide"
)

# Carrega variáveis de ambiente
load_dotenv()

class FootballDataClient:
    """Cliente para acessar dados de futebol da API"""
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    
    def get_competitions(self) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/competitions")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao buscar competições: {str(e)}")
            return []
    
    def get_matches(self, competition_id: str, season: str) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/competitions/{competition_id}/seasons/{season}/matches"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao buscar partidas: {str(e)}")
            return []
    
    def get_match_details(self, match_id: str) -> Dict:
        try:
            response = requests.get(f"{self.base_url}/matches/{match_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro ao buscar detalhes da partida: {str(e)}")
            return {}

class FootballAnalysisTools:
    """Ferramentas para análise de futebol"""
    
    def __init__(self, data_client: FootballDataClient):
        self.client = data_client
    
    def get_tools(self) -> List[Tool]:
        return [
            Tool(
                name="get_match_events",
                func=self._get_match_events,
                description="Obtém eventos de uma partida específica (gols, cartões, substituições)"
            ),
            Tool(
                name="analyze_player",
                func=self._analyze_player,
                description="Analisa estatísticas e desempenho de um jogador específico na partida"
            ),
            Tool(
                name="compare_players",
                func=self._compare_players,
                description="Compara estatísticas entre dois jogadores da partida"
            ),
            Tool(
                name="get_match_stats",
                func=self._get_match_stats,
                description="Obtém estatísticas gerais da partida (posse, chutes, etc)"
            )
        ]

    def _get_match_events(self, match_id: str) -> str:
        """Processa e retorna eventos da partida"""
        data = self.client.get_match_details(match_id)
        events = data.get("events", [])
        formatted_events = []
        
        for event in events:
            formatted_event = (
                f"{event.get('time')}' - "
                f"{event.get('type')}: "
                f"{event.get('player', 'N/A')} "
                f"({event.get('team', 'N/A')})"
            )
            formatted_events.append(formatted_event)
        
        return "\n".join(formatted_events)
    
    def _analyze_player(self, query: str) -> str:
        """Analisa estatísticas do jogador"""
        try:
            match_id, player_name = query.split(":", 1)
            data = self.client.get_match_details(match_id)
            # Implementação da análise do jogador
            player_stats = self._find_player_stats(data, player_name)
            return json.dumps(player_stats, indent=2)
        except Exception as e:
            return f"Erro ao analisar jogador: {str(e)}"
    
    def _compare_players(self, query: str) -> str:
        """Compara estatísticas entre jogadores"""
        try:
            match_id, players = query.split(":", 1)
            player1, player2 = players.split(",")
            data = self.client.get_match_details(match_id)
            # Implementação da comparação
            stats1 = self._find_player_stats(data, player1)
            stats2 = self._find_player_stats(data, player2)
            return json.dumps({"player1": stats1, "player2": stats2}, indent=2)
        except Exception as e:
            return f"Erro na comparação: {str(e)}"
    
    def _get_match_stats(self, match_id: str) -> str:
        """Retorna estatísticas gerais da partida"""
        data = self.client.get_match_details(match_id)
        return json.dumps(data.get("stats", {}), indent=2)
    
    def _find_player_stats(self, match_data: Dict, player_name: str) -> Dict:
        """Encontra estatísticas de um jogador específico"""
        # Implementar lógica de busca de estatísticas
        return {}

class FootballAnalysisAgent:
    """Agente de análise usando LangChain ReAct"""
    
    def __init__(self, tools: List[Tool]):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=2048
        )
        
        # Define templates para diferentes tipos de análise
        self.templates = {
            "analysis": ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(
                    "Você é um analista de futebol especializado. Analise os dados fornecidos de forma profissional e detalhada."
                ),
                HumanMessagePromptTemplate.from_template("{input}")
            ]),
            "narrative": ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(
                    "Você é um narrador de futebol com estilo {style}. "
                    "Crie uma narrativa envolvente dos eventos da partida."
                ),
                HumanMessagePromptTemplate.from_template("{input}")
            ])
        }
        
        self.tools = tools
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.agent = ReActDocstoreAgent.from_llm_and_tools(
            llm=self.llm,
            tools=tools,
            memory=self.memory,
            verbose=True
        )
        
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3
        )
    
    def analyze(self, query: str, style: str = None) -> str:
        """Executa análise usando o agente"""
        try:
            if style:
                prompt = self.templates["narrative"].format(
                    style=style,
                    input=query
                )
            else:
                prompt = self.templates["analysis"].format(
                    input=query
                )
            
            return self.agent_executor.run(prompt)
        except Exception as e:
            return f"Erro na análise: {str(e)}"

class FootballAnalysisApp:
    """Aplicação Streamlit para análise de futebol"""
    
    def __init__(self):
        self.data_client = FootballDataClient()
        self.tools = FootballAnalysisTools(self.data_client)
        self.agent = FootballAnalysisAgent(self.tools.get_tools())
        
        # Inicializar estado da sessão
        if 'selected_competition' not in st.session_state:
            st.session_state.selected_competition = None
        if 'selected_season' not in st.session_state:
            st.session_state.selected_season = None
        if 'selected_match' not in st.session_state:
            st.session_state.selected_match = None
    
    def main(self):
        st.title("⚽ Análise de Partidas de Futebol")
        
        # Sidebar para seleção
        with st.sidebar:
            self.show_match_selector()
        
        if st.session_state.selected_match:
            tabs = st.tabs([
                "Visão Geral",
                "Análise de Jogador",
                "Análise Narrativa",
                "Análise Inteligente"
            ])
            
            with tabs[0]:
                self.show_match_overview()
            with tabs[1]:
                self.show_player_analysis()
            with tabs[2]:
                self.show_narrative_analysis()
            with tabs[3]:
                self.show_intelligent_analysis()
        else:
            st.info("👈 Selecione uma partida no menu lateral para começar a análise")
    
    # [Restante dos métodos permanecem iguais...]

if __name__ == "__main__":
    app = FootballAnalysisApp()
    app.main()