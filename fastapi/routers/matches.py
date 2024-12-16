from fastapi import APIRouter, HTTPException
from models.match import MatchSummary
from utils.statsbomb import get_match_data
from utils.llm import generate_match_summary

router = APIRouter()

@router.get("/{match_id}/summary", response_model=MatchSummary)
async def get_match_summary(match_id: str):
    """
    Retorna um resumo da partida especificada.
    """
    try:
        # Implementar lógica de busca e processamento
        return {"message": "Endpoint em desenvolvimento"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
