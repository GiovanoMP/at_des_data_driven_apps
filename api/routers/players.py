from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
from api.utils.statsbomb_data import get_matches, get_match_lineup, get_player_stats

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/players", tags=["players"])

@router.get("/", response_model=List[Dict[str, Any]])
async def list_players(
    match_id: Optional[int] = Query(None, description="ID da partida para filtrar jogadores")
) -> List[Dict[str, Any]]:
    """
    Retorna a lista de todos os jogadores disponíveis.
    """
    try:
        if not match_id:
            # Usar a partida Inglaterra x Colômbia como padrão
            match_id = 7585
            
        # Obter detalhes da partida
        matches = get_matches(43, 3)  # Copa do Mundo 2018
        match = next((m for m in matches if m.get("match_id") == match_id), None)
        
        if not match:
            raise HTTPException(status_code=404, detail=f"Partida {match_id} não encontrada")
            
        # Obter lineups de ambos os times
        home_team = match.get("home_team")
        away_team = match.get("away_team")
        
        home_lineup = get_match_lineup(match_id, home_team)
        away_lineup = get_match_lineup(match_id, away_team)
        
        # Combinar os lineups
        all_players = []
        if home_lineup:
            all_players.extend(home_lineup)
        if away_lineup:
            all_players.extend(away_lineup)
            
        if not all_players:
            raise HTTPException(status_code=404, detail="Nenhum jogador encontrado")
            
        # Remover duplicatas baseado no player_id
        unique_players = {
            player["player_id"]: player 
            for player in all_players
        }.values()
        
        return list(unique_players)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao listar jogadores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar jogadores: {str(e)}")

@router.get("/{player_id}/profile", response_model=Dict[str, Any])
async def get_player_profile(
    player_id: int,
    match_id: Optional[int] = Query(None, description="ID da partida para obter estatísticas específicas")
) -> Dict[str, Any]:
    """
    Retorna o perfil detalhado de um jogador.
    """
    try:
        if not match_id:
            # Usar a partida Inglaterra x Colômbia como padrão
            match_id = 7585
            
        # Obter estatísticas do jogador
        stats = get_player_stats(match_id, player_id)
        
        if not stats:
            raise HTTPException(
                status_code=404,
                detail=f"Jogador com ID {player_id} não encontrado na partida {match_id}"
            )
            
        return stats
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao obter perfil do jogador {player_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter perfil do jogador: {str(e)}"
        )
