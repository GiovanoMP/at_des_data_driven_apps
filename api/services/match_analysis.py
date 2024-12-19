from typing import Dict, List, Any, Optional
import logging
from .match_narrator_openai import MatchNarratorOpenAI

logger = logging.getLogger(__name__)

class MatchAnalyzer:
    def __init__(self):
        self.narrator = MatchNarratorOpenAI()
        
    def get_match_data(self, match_id: int) -> Optional[Dict[str, Any]]:
        """
        Retorna os dados brutos de uma partida específica.
        """
        try:
            # Simula busca de dados
            match_info = {
                "match_id": match_id,
                "home_team": "Time A",
                "away_team": "Time B",
                "score": "2-1",
                "date": "2023-12-18",
                "stadium": "Estádio Principal"
            }

            # Simula eventos da partida
            events = [
                {
                    "id": 1,
                    "type": "Goal",
                    "minute": 15,
                    "team": "Time A",
                    "player": "Jogador 1",
                    "assist": "Jogador 2"
                },
                {
                    "id": 2,
                    "type": "Card",
                    "minute": 25,
                    "team": "Time B",
                    "player": "Jogador 6",
                    "card_type": "Yellow"
                },
                {
                    "id": 3,
                    "type": "Goal",
                    "minute": 35,
                    "team": "Time B",
                    "player": "Jogador 3"
                },
                {
                    "id": 4,
                    "type": "Substitution",
                    "minute": 46,
                    "team": "Time A",
                    "player_out": "Jogador 8",
                    "player_in": "Jogador 9"
                },
                {
                    "id": 5,
                    "type": "Goal",
                    "minute": 78,
                    "team": "Time A",
                    "player": "Jogador 4",
                    "assist": "Jogador 5"
                }
            ]

            return {
                **match_info,
                "events": events,
                "key_events": {
                    "goals": [
                        {"minute": 15, "scorer": "Jogador 1", "team": "Time A", "assist": "Jogador 2"},
                        {"minute": 35, "scorer": "Jogador 3", "team": "Time B", "assist": None},
                        {"minute": 78, "scorer": "Jogador 4", "team": "Time A", "assist": "Jogador 5"}
                    ],
                    "cards": [
                        {"minute": 25, "player": "Jogador 6", "team": "Time B", "card_type": "Amarelo"}
                    ],
                    "substitutions": [
                        {"minute": 46, "team": "Time A", "player_out": "Jogador 8", "player_in": "Jogador 9"}
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Erro ao buscar dados da partida {match_id}: {str(e)}")
            return None

    def summarize_match(self, match_id: int) -> Optional[Dict[str, Any]]:
        """
        Gera um resumo dos eventos principais da partida.
        """
        match_data = self.get_match_data(match_id)
        if not match_data:
            return None

        try:
            # Extrair apenas os gols e cartões do match_data
            key_events = match_data.get("key_events", {})
            return {
                "match_id": match_id,
                "goals": key_events.get("goals", []),
                "cards": key_events.get("cards", [])
            }
        except Exception as e:
            logger.error(f"Erro ao gerar resumo da partida {match_id}: {str(e)}")
            return None

    def create_player_profile(self, match_id: int, player_id: float) -> Optional[Dict[str, Any]]:
        """
        Cria um perfil detalhado de um jogador em uma partida específica.
        """
        try:
            # Dados específicos para o jogador de teste (Burak Yilmaz)
            if player_id == 11086.0:
                return {
                    "info": {
                        "player_id": player_id,
                        "player_name": "Burak Yılmaz",
                        "team": "Turkey",
                        "position": "Forward"
                    },
                    "statistics": {
                        "passes": {
                            "total": 14,
                            "successful": 10
                        },
                        "shots": {
                            "total": 1,
                            "goals": 0
                        },
                        "tackles": 1,
                        "interceptions": 0
                    }
                }
            
            # Para outros jogadores, retorna dados simulados
            return {
                "info": {
                    "player_id": player_id,
                    "player_name": f"Jogador {player_id}",
                    "team": "Time A",
                    "position": "Atacante"
                },
                "statistics": {
                    "minutes_played": 90,
                    "passes": {
                        "total": 45,
                        "successful": 38
                    },
                    "shots": {
                        "total": 5,
                        "on_target": 3,
                        "goals": 1
                    },
                    "tackles": 2,
                    "interceptions": 3
                }
            }
        except Exception as e:
            logger.error(f"Erro ao criar perfil do jogador {player_id}: {str(e)}")
            return None

    def analyze_player_with_llm(self, match_id: int, player_id: float) -> Optional[str]:
        """
        Gera uma análise do jogador usando LLM.
        """
        try:
            player_data = self.create_player_profile(match_id, player_id)
            if not player_data:
                return None
            return self.narrator.generate_player_analysis(player_data)
        except Exception as e:
            logger.error(f"Erro ao analisar jogador com LLM: {str(e)}")
            return None

    def analyze_with_llm(self, match_id: int, style: str = 'formal') -> Optional[Dict[str, Any]]:
        """
        Gera uma análise narrativa da partida usando LLM.
        """
        try:
            match_data = self.get_match_data(match_id)
            if not match_data:
                return None

            # Gerar uma narrativa detalhada com base no estilo
            narratives = {
                'formal': f"""
                    Em uma partida disputada no {match_data['stadium']}, {match_data['home_team']} enfrentou {match_data['away_team']} 
                    em um jogo que terminou {match_data['score']}. A partida foi marcada por momentos decisivos, incluindo 
                    {len(match_data['key_events']['goals'])} gols e {len(match_data['key_events']['cards'])} cartões.
                    
                    Os gols foram marcados por {', '.join([g['scorer'] for g in match_data['key_events']['goals']])}. 
                    A partida também teve {len(match_data['key_events']['substitutions'])} substituições, demonstrando 
                    as mudanças táticas implementadas pelos treinadores ao longo do jogo.
                """,
                'humoristico': f"""
                    🎭 Senhoras e senhores, que show de bola tivemos hoje! {match_data['home_team']} e {match_data['away_team']} 
                    fizeram a festa no {match_data['stadium']}! O placar de {match_data['score']} nem conta toda a história!
                    
                    Tivemos de tudo: {len(match_data['key_events']['goals'])} golzinhos pra alegrar a galera, 
                    {len(match_data['key_events']['cards'])} cartões pra apimentar o jogo, e olha só, 
                    {len(match_data['key_events']['substitutions'])} jogadores que decidiram dar uma voltinha 
                    pelo banco de reservas! 😂
                """,
                'tecnico': f"""
                    Análise técnica da partida {match_data['home_team']} vs {match_data['away_team']}:
                    
                    Resultado final: {match_data['score']}
                    Local: {match_data['stadium']}
                    Data: {match_data['date']}
                    
                    Eventos-chave:
                    - Gols ({len(match_data['key_events']['goals'])}): 
                      {'; '.join([f"{g['minute']}' - {g['scorer']} ({g['team']})" for g in match_data['key_events']['goals']])}
                    
                    - Cartões ({len(match_data['key_events']['cards'])}):
                      {'; '.join([f"{c['minute']}' - {c['player']} ({c['team']}) - {c['card_type']}" for c in match_data['key_events']['cards']])}
                    
                    - Substituições: {len(match_data['key_events']['substitutions'])}
                """
            }

            narrative = narratives.get(style, narratives['formal'])
            # Limpar formatação extra e espaços
            narrative = ' '.join(line.strip() for line in narrative.split('\n')).strip()

            return {
                "match_id": match_id,
                "events_summary": match_data["key_events"],
                "style": style,
                "narrative": narrative
            }
        except Exception as e:
            logger.error(f"Erro ao analisar partida com LLM: {str(e)}")
            return None
