from fastapi import APIRouter, HTTPException
from models.narrative import MatchNarrative
from utils.llm import generate_narrative

router = APIRouter()

@router.get("/{match_id}", response_model=MatchNarrative)
async def get_match_narrative(match_id: str, style: str = "formal"):
    """
    Gera uma narrativa da partida no estilo especificado.
    Estilos disponíveis: formal, humorístico, técnico
    """
    try:
        # Implementar lógica de geração de narrativa
        return {"message": "Endpoint em desenvolvimento"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
