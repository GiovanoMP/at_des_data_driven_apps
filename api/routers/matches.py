from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from api.services.match_analysis import MatchAnalyzer
from api.services.match_narrator import MatchNarrator
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])

# Instanciar serviços
match_analyzer = MatchAnalyzer()
match_narrator = MatchNarrator()

class NarrationStyle(str, Enum):
    formal = "formal"
    humorous = "humorous"
    technical = "technical"

@router.get("/{match_id}")
async def get_match(match_id: int) -> Dict[str, Any]:
    """
    Retorna os dados brutos de uma partida específica.
    """
    match_data = match_analyzer.get_match_data(match_id)
    if not match_data:
        raise HTTPException(
            status_code=404,
            detail=f"Partida {match_id} não encontrada"
        )
    return match_data

@router.get("/{match_id}/summary")
async def get_match_summary(match_id: int) -> Dict[str, Any]:
    """
    Retorna um resumo estruturado da partida.
    """
    summary = match_analyzer.summarize_match(match_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível gerar o resumo da partida {match_id}"
        )
    return summary

@router.get("/{match_id}/narrative")
async def get_match_narrative(
    match_id: int,
    style: NarrationStyle = NarrationStyle.formal
) -> Dict[str, str]:
    """
    Gera uma narrativa da partida no estilo especificado.
    """
    summary = match_analyzer.summarize_match(match_id)
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível encontrar dados da partida {match_id}"
        )
        
    narrative = match_narrator.generate_narrative(summary, style=style)
    return {"narrative": narrative}

@router.get("/{match_id}/player/{player_id}")
async def get_player_profile(
    match_id: int,
    player_id: int,
    include_analysis: bool = False
) -> Dict[str, Any]:
    """
    Retorna o perfil detalhado de um jogador em uma partida específica.
    """
    profile = match_analyzer.create_player_profile(match_id, player_id)
    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível encontrar o jogador {player_id} na partida {match_id}"
        )
        
    if include_analysis:
        analysis = match_narrator.generate_player_analysis(profile)
        profile['analysis'] = analysis
        
    return profile

@router.get("/{match_id}/analysis")
async def get_match_analysis(match_id: int) -> Dict[str, Any]:
    """
    Retorna uma análise tática detalhada da partida usando LLM.
    """
    analysis = match_analyzer.analyze_with_llm(match_id)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível gerar a análise da partida {match_id}"
        )
    return analysis

@router.get("/{match_id}/players/{player_id}/analysis")
async def get_player_match_analysis(
    match_id: int,
    player_id: int
) -> Dict[str, Any]:
    """
    Retorna uma análise detalhada do desempenho do jogador na partida usando LLM.
    """
    analysis = match_analyzer.analyze_player_with_llm(match_id, player_id)
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Não foi possível gerar a análise do jogador {player_id} na partida {match_id}"
        )
    return analysis
