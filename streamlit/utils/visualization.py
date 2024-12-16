import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configura o Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def create_player_stats_plot(player_stats: Dict) -> go.Figure:
    """
    Cria visualizações para estatísticas dos jogadores.
    """
    try:
        # Converte as estatísticas para um formato adequado para visualização
        stats_df = pd.DataFrame(list(player_stats['statistics'].items()), 
                              columns=['Metric', 'Value'])
        
        # Cria o gráfico de barras
        fig = px.bar(stats_df, x='Metric', y='Value',
                    title=f"Estatísticas do Jogador: {player_stats.get('name', 'N/A')}")
        
        # Personaliza o layout
        fig.update_layout(
            xaxis_title="Métricas",
            yaxis_title="Valores",
            showlegend=False
        )
        
        return fig
    except Exception as e:
        raise Exception(f"Erro ao criar visualização: {str(e)}")

def generate_plot_description(fig: go.Figure, player_stats: Dict) -> str:
    """
    Usa o Gemini para gerar uma descrição da visualização.
    """
    try:
        prompt = f"""
        Analise as seguintes estatísticas do jogador e gere uma descrição concisa:
        
        Jogador: {player_stats.get('name', 'N/A')}
        Time: {player_stats.get('team', 'N/A')}
        Estatísticas:
        {player_stats.get('statistics', {})}
        
        Por favor, destaque os pontos mais relevantes do desempenho do jogador.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Erro ao gerar descrição: {str(e)}")
