from statsbombpy import sb
from typing import Dict, List, Any, Optional
import pandas as pd
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StatsBombHandler:
    """
    Classe para gerenciar todas as interações com a API StatsBomb.
    Centraliza as chamadas e tratamento de dados da API.
    """
    
    @staticmethod
    def get_match_data(match_id: int) -> Dict[str, Any]:
        """
        Recupera os dados brutos de uma partida específica.
        
        Args:
            match_id: ID da partida na StatsBomb
            
        Returns:
            Dictionary com os dados da partida
            
        Raises:
            Exception: Se houver erro ao buscar os dados
        """
        try:
            logger.info(f"Buscando dados da partida {match_id}")
            events = sb.events(match_id=match_id)
            lineup = sb.lineups(match_id=match_id)
            
            # Converte DataFrames para dicionários
            events_dict = events.to_dict('records') if not events.empty else []
            lineup_dict = {team: players.to_dict('records') 
                         for team, players in lineup.items()}
            
            return {
                "match_id": match_id,
                "events": events_dict,
                "lineup": lineup_dict
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados da partida {match_id}: {str(e)}")
            raise Exception(f"Falha ao recuperar dados da partida: {str(e)}")
    
    @staticmethod
    def get_player_stats(match_id: int, player_id: int) -> Dict[str, Any]:
        """
        Calcula estatísticas de um jogador em uma partida específica.
        
        Args:
            match_id: ID da partida
            player_id: ID do jogador
            
        Returns:
            Dictionary com estatísticas do jogador
        """
        try:
            logger.info(f"Calculando estatísticas do jogador {player_id} na partida {match_id}")
            events = sb.events(match_id=match_id)
            
            # Filtra eventos do jogador
            player_events = events[events['player_id'] == player_id]
            
            # Calcula estatísticas básicas
            stats = {
                'passes_completed': len(player_events[
                    (player_events['type'] == 'Pass') & 
                    (player_events['outcome'] == 'Complete')
                ]),
                'shots': len(player_events[player_events['type'] == 'Shot']),
                'goals': len(player_events[
                    (player_events['type'] == 'Shot') & 
                    (player_events['outcome'] == 'Goal')
                ]),
                'tackles': len(player_events[player_events['type'] == 'Tackle']),
                'interceptions': len(player_events[player_events['type'] == 'Interception'])
            }
            
            # Adiciona informações do jogador
            player_info = player_events.iloc[0] if not player_events.empty else {}
            return {
                'player_id': player_id,
                'name': player_info.get('player_name', 'Unknown'),
                'team': player_info.get('team_name', 'Unknown'),
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas do jogador {player_id}: {str(e)}")
            raise Exception(f"Falha ao calcular estatísticas do jogador: {str(e)}")
