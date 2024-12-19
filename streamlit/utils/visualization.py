import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
import openai
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configura a OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

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

def create_player_stats_radar(stats: Dict) -> go.Figure:
    """
    Cria um gráfico radar com as estatísticas do jogador.
    """
    try:
        # Prepara os dados para o gráfico radar
        categories = list(stats.keys())
        values = list(stats.values())
        
        # Cria o gráfico radar
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=f'Estatísticas'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2]
                )),
            showlegend=True
        )
        
        return fig
    except Exception as e:
        raise Exception(f"Erro ao criar gráfico radar: {str(e)}")

def generate_plot_description(fig: go.Figure, player_stats: Dict) -> str:
    """
    Usa a OpenAI para gerar uma descrição da visualização.
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
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um analista esportivo especializado em estatísticas de futebol."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro ao gerar descrição: {str(e)}")

def create_match_timeline(events: List[Dict]) -> go.Figure:
    """
    Cria uma linha do tempo dos eventos da partida.
    """
    try:
        # Prepara os dados para a linha do tempo
        df = pd.DataFrame(events)
        
        # Cria o gráfico de linha do tempo
        fig = px.scatter(df, 
                        x='minute',
                        y='type',
                        color='team',
                        hover_data=['player', 'outcome'])
        
        fig.update_layout(
            title='Linha do Tempo da Partida',
            xaxis_title='Minuto',
            yaxis_title='Tipo de Evento'
        )
        
        return fig
    except Exception as e:
        raise Exception(f"Erro ao criar linha do tempo: {str(e)}")
