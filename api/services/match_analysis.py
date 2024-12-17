from typing import Dict, List, Any, Optional
import logging
from statsbombpy import sb
import pandas as pd
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

logger = logging.getLogger(__name__)

class MatchAnalyzer:
    def __init__(self):
        self.cache = {}  # Cache simples para evitar chamadas repetidas à API
        
        # Configurar o Gemini
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    def get_match_data(self, match_id: int) -> Dict[str, Any]:
        """
        Obtém os dados brutos de uma partida específica.
        """
        cache_key = f"match_{match_id}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Primeiro, precisamos encontrar a competição correta
            competitions = sb.competitions()
            match_found = None
            
            for _, comp in competitions.iterrows():
                matches = sb.matches(competition_id=comp['competition_id'], 
                                  season_id=comp['season_id'])
                if matches is None or matches.empty:
                    continue
                    
                match = matches[matches['match_id'] == match_id]
                if not match.empty:
                    match_found = match.iloc[0].to_dict()
                    break

            if not match_found:
                return None

            # Obter eventos da partida
            events = sb.events(match_id=match_id)
            if events is not None and not events.empty:
                events = events.fillna('')

            # Obter lineups
            lineups = sb.lineups(match_id=match_id)

            match_data = {
                'match_info': match_found,
                'events': events.to_dict('records') if events is not None else [],
                'lineups': {
                    team: lineup.to_dict('records') 
                    for team, lineup in lineups.items()
                } if lineups else {}
            }

            self.cache[cache_key] = match_data
            return match_data

        except Exception as e:
            logger.error(f"Erro ao obter dados da partida {match_id}: {str(e)}")
            return None

    def create_player_profile(self, match_id: int, player_id: float) -> Dict[str, Any]:
        """
        Cria um perfil detalhado de um jogador em uma partida específica.
        """
        match_data = self.get_match_data(match_id)
        if not match_data or 'events' not in match_data:
            return None

        events_df = pd.DataFrame(match_data['events'])
        
        # Filtrar eventos do jogador usando player_id (que é float na StatsBomb)
        player_events = events_df[events_df['player_id'] == player_id]

        if player_events.empty:
            return None

        # Obter informações básicas do jogador
        player_info = {
            'player_id': player_id,
            'player_name': player_events.iloc[0]['player'],
            'team': player_events.iloc[0]['team']
        }

        # Calcular estatísticas
        stats = {
            'passes': {
                'total': len(player_events[player_events['type'] == 'Pass']),
                'successful': len(player_events[(player_events['type'] == 'Pass') & 
                                             (player_events['pass_outcome'].isna())])
            },
            'shots': {
                'total': len(player_events[player_events['type'] == 'Shot']),
                'goals': len(player_events[(player_events['type'] == 'Shot') & 
                                        (player_events['shot_outcome'] == 'Goal')])
            },
            'tackles': len(player_events[player_events['type'] == 'Duel']),
            'interceptions': len(player_events[player_events['type'] == 'Interception']),
            'minutes_played': self._calculate_minutes_played(player_events)
        }

        return {
            'info': player_info,
            'statistics': stats,
            'events': player_events.to_dict('records')
        }

    def summarize_match(self, match_id: int):
        """
        Cria um resumo dos principais eventos da partida.
        """
        events = sb.events(match_id=match_id)
        
        # Filtrar gols
        goals = events[(events['type'] == 'Shot') & (events['shot_outcome'] == 'Goal')]
        
        # Filtrar cartões
        cards = events[events['foul_committed_card'].notna()]

        match_info = {
            'match_id': match_id,
            'goals': [],
            'cards': []
        }

        # Processar gols
        for _, row in goals.iterrows():
            goal = {
                'minute': int(row['minute']),
                'team': str(row['team']),
                'scorer': str(row['player']),
                'assist': ''
            }
            match_info['goals'].append(goal)

        # Processar cartões
        for _, row in cards.iterrows():
            card = {
                'minute': int(row['minute']),
                'team': str(row['team']),
                'player': str(row['player']),
                'card_type': str(row['foul_committed_card'])
            }
            match_info['cards'].append(card)

        return match_info

    def analyze_with_llm(self, match_id: int, style: str = 'formal') -> dict:
        """
        Realiza uma análise tática aprofundada da partida usando LLM.
        
        Args:
            match_id: ID da partida
            style: Estilo de narração ('formal', 'humoristico', 'tecnico')
        """
        summary = self.summarize_match(match_id)
        if not summary:
            return None

        # Preparar o prompt para o LLM
        goals_text = ""
        for goal in summary['goals']:
            goals_text += f"- Gol marcado por {goal['scorer']} ({goal['team']}) no minuto {goal['minute']}\n"

        cards_text = ""
        for card in summary['cards']:
            cards_text += f"- {card['card_type']} para {card['player']} ({card['team']}) no minuto {card['minute']}\n"

        style_instructions = {
            'formal': """Forneça uma análise formal e profissional da partida, mantendo um tom sério e objetivo.
                       Foque em fatos e estatísticas, evitando linguagem coloquial.""",
            'humoristico': """Faça uma narração bem-humorada e descontraída da partida.
                            Use trocadilhos, analogias divertidas e mantenha um tom leve e entertaining.
                            Seja criativo mas mantenha o respeito aos jogadores e times.""",
            'tecnico': """Realize uma análise técnica profunda da partida.
                        Foque em aspectos táticos, formações, padrões de jogo e decisões técnicas.
                        Use terminologia específica do futebol e explique conceitos avançados."""
        }

        prompt = f"""Analise esta partida de futebol com base nos seguintes eventos:

Gols:
{goals_text}

Cartões:
{cards_text}

{style_instructions.get(style, style_instructions['formal'])}

Por favor, forneça:
1. Um resumo da partida no estilo solicitado
2. Os momentos-chave e sua importância
3. Análise do desempenho das equipes
4. Conclusão e destaques

Mantenha a análise concisa e focada nos eventos mais importantes."""

        try:
            response = self.model.generate_content(prompt)
            return {
                'match_id': match_id,
                'events_summary': summary,
                'style': style,
                'narrative': response.text
            }
        except Exception as e:
            logging.error(f"Erro ao gerar análise com LLM: {str(e)}")
            return None

    def analyze_player_with_llm(self, match_id: int, player_id: float) -> Dict[str, Any]:
        """
        Realiza uma análise detalhada do desempenho do jogador usando LLM.
        """
        player_profile = self.create_player_profile(match_id, player_id)
        if not player_profile:
            return None

        # Preparar estatísticas para o prompt
        stats = player_profile['statistics']
        passes = stats['passes']
        shots = stats['shots']

        prompt = f"""
        Atue como um analista profissional de desempenho de jogadores. Analise o seguinte jogador:

        Jogador: {player_profile['info']['player_name']}
        Time: {player_profile['info']['team']}
        
        Estatísticas da Partida:
        - Minutos jogados: {stats['minutes_played']}
        - Passes: {passes['total']} (Completos: {passes['successful']})
        - Finalizações: {shots['total']} (Gols: {shots['goals']})
        - Desarmes: {stats['tackles']}
        - Interceptações: {stats['interceptions']}

        Por favor, forneça:
        1. Análise geral do desempenho
        2. Pontos fortes demonstrados
        3. Áreas para melhoria
        4. Comparação com o desempenho esperado para sua posição
        5. Recomendações específicas para desenvolvimento

        Base sua análise em dados estatísticos e padrões táticos observados.
        """

        try:
            response = self.model.generate_content(prompt)
            
            return {
                'player_id': player_id,
                'match_id': match_id,
                'performance_analysis': response.text,
                'statistics': player_profile
            }
        except Exception as e:
            logger.error(f"Erro na análise LLM do jogador {player_id}: {str(e)}")
            return None

    def create_match_summary(self, match_id: int) -> Dict[str, Any]:
        """
        Cria uma sumarização dos eventos principais da partida.
        """
        match_data = self.get_match_data(match_id)
        if not match_data or 'events' not in match_data:
            return None

        events_df = pd.DataFrame(match_data['events'])
        
        # Extrair informações básicas da partida
        teams = events_df['team'].unique()
        
        # Identificar gols
        goals = events_df[
            (events_df['type'] == 'Shot') & 
            (events_df['shot_outcome'] == 'Goal')
        ].apply(lambda x: {
            'team': x['team'],
            'player': x['player'],
            'minute': x['minute']
        }, axis=1).tolist()

        # Identificar cartões
        cards = events_df[
            events_df['type'] == 'Foul Committed'
        ].apply(lambda x: {
            'type': x.get('foul_committed_card', 'Yellow'),
            'team': x['team'],
            'player': x['player'],
            'minute': x['minute']
        }, axis=1).tolist()

        # Contar estatísticas por time
        team_stats = {}
        for team in teams:
            team_events = events_df[events_df['team'] == team]
            team_stats[team] = {
                'shots': len(team_events[team_events['type'] == 'Shot']),
                'passes': len(team_events[team_events['type'] == 'Pass']),
                'fouls': len(team_events[team_events['type'] == 'Foul Committed']),
                'tackles': len(team_events[team_events['type'] == 'Duel']),
                'goals': len(goals) if goals else 0
            }

        summary = {
            'match_id': match_id,
            'teams': list(teams),
            'goals': goals,
            'cards': cards,
            'team_stats': team_stats
        }

        # Gerar narrativa usando LLM
        prompt = f"""
        Crie uma sumarização clara e concisa desta partida de futebol:
        
        Times: {', '.join(teams)}
        
        Gols:
        {', '.join([f"{g['player']} ({g['team']}) - {g['minute']}'" for g in goals])}
        
        Cartões:
        {', '.join([f"{c['player']} ({c['team']}) - {c['type']} - {c['minute']}'" for c in cards])}
        
        Estatísticas por time:
        {json.dumps(team_stats, indent=2)}
        """

        try:
            narrative = self._generate_llm_response(prompt)
            summary['narrative'] = narrative
        except Exception as e:
            logger.error(f"Erro ao gerar narrativa: {str(e)}")
            summary['narrative'] = None

        return summary

    def _calculate_minutes_played(self, player_events: pd.DataFrame) -> int:
        """
        Calcula o número de minutos jogados por um jogador.
        """
        if player_events.empty:
            return 0

        # Verificar se o jogador foi substituído
        substitution = player_events[player_events['type'] == 'Substitution']
        if not substitution.empty:
            return int(substitution.iloc[0]['minute'])

        # Se não foi substituído, assumir que jogou a partida toda
        return 90  # Tempo padrão de uma partida

    def _generate_llm_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Erro ao gerar resposta do LLM: {str(e)}")
            return None
