from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from ..services.match_analysis import MatchAnalyzer

router = APIRouter()
analysis_service = MatchAnalyzer()

@router.get("/matches/{match_id}")
async def get_match_data(match_id: int) -> Dict[str, Any]:
    """
    Retorna os dados brutos de uma partida específica.
    """
    data = analysis_service.get_match_data(match_id)
    if not data:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return data

@router.get("/matches/{match_id}/summary")
async def get_match_summary(match_id: int) -> Dict[str, Any]:
    """
    Retorna uma sumarização dos eventos principais da partida.
    """
    summary = analysis_service.summarize_match(match_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Não foi possível gerar a sumarização da partida")
    return summary

@router.get("/matches/{match_id}/player/{player_id}")
async def get_player_profile(
    match_id: int, 
    player_id: float,
    include_analysis: bool = False
) -> Dict[str, Any]:
    """
    Retorna o perfil detalhado de um jogador em uma partida específica.
    """
    profile = analysis_service.create_player_profile(match_id, player_id)
    if not profile:
        raise HTTPException(
            status_code=404, 
            detail=f"Não foi possível encontrar o jogador {player_id} na partida {match_id}"
        )
    
    if include_analysis:
        analysis = analysis_service.analyze_player_with_llm(match_id, player_id)
        if analysis:
            profile['analysis'] = analysis
    
    return profile

@router.get("/matches/{match_id}/analysis")
async def get_match_analysis(
    match_id: int,
    style: str = 'formal'
) -> Dict[str, Any]:
    """
    Retorna uma análise narrativa da partida em um estilo específico.
    
    Args:
        match_id: ID da partida
        style: Estilo da narração ('formal', 'humoristico', 'tecnico')
    """
    if style not in ['formal', 'humoristico', 'tecnico']:
        raise HTTPException(
            status_code=400,
            detail="Estilo inválido. Use 'formal', 'humoristico' ou 'tecnico'"
        )
    
    analysis = analysis_service.analyze_with_llm(match_id, style)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Não foi possível gerar a análise da partida"
        )
    return analysis
