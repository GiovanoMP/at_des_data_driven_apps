from statsbombpy import sb
import pandas as pd
import logging
from typing import Dict, List, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_competitions() -> List[Dict[str, Any]]:
    """
    Retorna a lista de todas as competições disponíveis.
    """
    try:
        competitions = sb.competitions()
        if competitions is None or competitions.empty:
            logger.warning("Nenhuma competição encontrada")
            return []
            
        # Garantir que temos todas as colunas necessárias
        required_columns = ['competition_id', 'competition_name', 'season_id', 'season_name', 'country_name']
        for col in required_columns:
            if col not in competitions.columns:
                competitions[col] = ''
                
        competitions = competitions.fillna('')
        return competitions.to_dict('records')
    except Exception as e:
        logger.error(f"Erro ao obter competições: {str(e)}")
        return []

def get_matches(competition_id: int, season_id: int) -> List[Dict[str, Any]]:
    """
    Retorna a lista de partidas de uma competição e temporada específicas.
    """
    try:
        matches = sb.matches(competition_id=competition_id, season_id=season_id)
        if matches is None or matches.empty:
            logger.warning(f"Nenhuma partida encontrada para competition_id={competition_id}, season_id={season_id}")
            return []
            
        # Garantir que temos todas as colunas necessárias
        required_columns = [
            'match_id', 'match_date', 'match_time', 
            'home_team', 'away_team', 'home_score', 'away_score',
            'competition_stage', 'stadium', 'referee'
        ]
        for col in required_columns:
            if col not in matches.columns:
                matches[col] = ''
                
        matches = matches.fillna('')
        return matches.to_dict('records')
    except Exception as e:
        logger.error(f"Erro ao obter partidas: {str(e)}")
        return []

def get_match_events(match_id: int) -> List[Dict[str, Any]]:
    """
    Retorna todos os eventos de uma partida específica.
    """
    try:
        events = sb.events(match_id=match_id)
        if events is None or events.empty:
            logger.warning(f"Nenhum evento encontrado para match_id={match_id}")
            return []
            
        # Garantir que todos os campos necessários existam
        required_columns = [
            'id', 'type', 'minute', 'second',
            'team', 'player', 'position',
            'location', 'under_pressure', 'outcome'
        ]
        for col in required_columns:
            if col not in events.columns:
                events[col] = ''
                
        events = events.fillna('')
        return events.to_dict('records')
    except Exception as e:
        logger.error(f"Erro ao obter eventos da partida {match_id}: {str(e)}")
        return []

def get_match_lineup(match_id: int, team_name: str) -> List[Dict[str, Any]]:
    """
    Retorna o lineup de um time em uma partida específica.
    """
    try:
        lineups = sb.lineups(match_id=match_id)
        if lineups is None:
            logger.warning(f"Nenhum lineup encontrado para match_id={match_id}")
            return []
            
        # Tentar encontrar o time com diferentes variações do nome
        team_variations = [
            team_name,
            team_name.title(),
            team_name.upper(),
            team_name.lower(),
            team_name.strip()
        ]
        
        for team_var in team_variations:
            if team_var in lineups:
                team_lineup = lineups[team_var]
                if team_lineup is not None and not team_lineup.empty:
                    # Garantir que todos os campos necessários existam
                    required_columns = [
                        'player_id', 'player_name', 'player_nickname',
                        'jersey_number', 'position', 'starting'
                    ]
                    for col in required_columns:
                        if col not in team_lineup.columns:
                            team_lineup[col] = ''
                            
                    team_lineup = team_lineup.fillna('')
                    return team_lineup.to_dict('records')
                
        logger.warning(f"Time {team_name} não encontrado nos lineups")
        return []
    except Exception as e:
        logger.error(f"Erro ao obter lineup da partida {match_id}, time {team_name}: {str(e)}")
        return []

def get_player_stats(match_id: int, player_id: int) -> Optional[Dict[str, Any]]:
    """
    Retorna estatísticas de um jogador em uma partida específica.
    """
    try:
        events = sb.events(match_id=match_id)
        player_events = events[events['player_id'] == player_id]
        
        if player_events.empty:
            return None
            
        stats = {
            'player_id': player_id,
            'player_name': player_events.iloc[0].get('player', ''),
            'team': player_events.iloc[0].get('team', ''),
            'total_passes': len(player_events[player_events['type'] == 'Pass']),
            'successful_passes': len(player_events[(player_events['type'] == 'Pass') & (player_events['pass_outcome'].isna())]),
            'shots': len(player_events[player_events['type'] == 'Shot']),
            'goals': len(player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'Goal')]),
            'assists': len(player_events[player_events['pass_shot_assist'] == True]),
            'tackles': len(player_events[player_events['type'] == 'Duel']),
            'interceptions': len(player_events[player_events['type'] == 'Interception'])
        }
        
        return stats
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do jogador {player_id}: {str(e)}")
        return None
