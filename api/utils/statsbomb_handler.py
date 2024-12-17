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

    @staticmethod
    def get_matches(competition_id: Optional[int] = None, season_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Recupera lista de partidas, opcionalmente filtradas por competição e temporada.
        
        Args:
            competition_id: ID opcional da competição para filtrar
            season_id: ID opcional da temporada para filtrar
            
        Returns:
            Lista de partidas
        """
        try:
            logger.info(f"Buscando partidas - competition_id: {competition_id}, season_id: {season_id}")
            matches = sb.matches(competition_id=competition_id, season_id=season_id)
            
            # Converter DataFrame para lista de dicionários
            matches_list = matches.to_dict('records') if not matches.empty else []
            
            return matches_list
            
        except Exception as e:
            logger.error(f"Erro ao buscar partidas: {str(e)}")
            raise Exception(f"Falha ao recuperar lista de partidas: {str(e)}")
    
    @staticmethod
    def get_match_events(match_id: int) -> List[Dict[str, Any]]:
        """
        Recupera todos os eventos de uma partida específica.
        
        Args:
            match_id: ID da partida
            
        Returns:
            Lista de eventos da partida
        """
        try:
            logger.info(f"Buscando eventos da partida {match_id}")
            events = sb.events(match_id=match_id)
            
            # Converter DataFrame para lista de dicionários
            events_list = events.to_dict('records') if not events.empty else []
            
            return events_list
            
        except Exception as e:
            logger.error(f"Erro ao buscar eventos da partida {match_id}: {str(e)}")
            raise Exception(f"Falha ao recuperar eventos da partida: {str(e)}")
    
    @staticmethod
    def get_match_lineup(match_id: int, team: str, include_stats: bool = False) -> List[Dict[str, Any]]:
        """
        Recupera o lineup de um time específico em uma partida.
        
        Args:
            match_id: ID da partida
            team: Nome do time
            include_stats: Se deve incluir estatísticas dos jogadores
            
        Returns:
            Lista de jogadores com suas informações
        """
        try:
            logger.info(f"Buscando lineup da partida {match_id} para o time {team}")
            lineup = sb.lineups(match_id=match_id)
            
            if team not in lineup:
                raise Exception(f"Time {team} não encontrado na partida {match_id}")
            
            team_lineup = lineup[team]
            players_list = team_lineup.to_dict('records') if not team_lineup.empty else []
            
            if include_stats:
                # Adicionar estatísticas para cada jogador
                events = sb.events(match_id=match_id)
                for player in players_list:
                    player_events = events[events['player_id'] == player['player_id']]
                    player['statistics'] = StatsBombHandler._calculate_player_stats(player_events)
            
            return players_list
            
        except Exception as e:
            logger.error(f"Erro ao buscar lineup: {str(e)}")
            raise Exception(f"Falha ao recuperar lineup: {str(e)}")
    
    @staticmethod
    def _calculate_player_stats(player_events: pd.DataFrame) -> Dict[str, int]:
        """
        Calcula estatísticas básicas de um jogador a partir de seus eventos.
        
        Args:
            player_events: DataFrame com eventos do jogador
            
        Returns:
            Dicionário com estatísticas calculadas
        """
        return {
            "passes_completed": len(player_events[
                (player_events['type'] == 'Pass') & 
                (player_events['outcome'] == 'Complete')
            ]),
            "shots": len(player_events[player_events['type'] == 'Shot']),
            "goals": len(player_events[
                (player_events['type'] == 'Shot') & 
                (player_events['outcome'] == 'Goal')
            ]),
            "tackles": len(player_events[player_events['type'] == 'Tackle']),
            "interceptions": len(player_events[player_events['type'] == 'Interception'])
        }
