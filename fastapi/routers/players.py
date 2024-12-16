from fastapi import APIRouter, HTTPException
from models.player import PlayerProfile
from utils.statsbomb import get_player_stats

router = APIRouter()

@router.get("/{player_id}/profile", response_model=PlayerProfile)
async def get_player_profile(player_id: str):
    """
    Retorna o perfil detalhado de um jogador.
    """
    try:
        # Implementar lógica de busca e processamento
        return {"message": "Endpoint em desenvolvimento"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
