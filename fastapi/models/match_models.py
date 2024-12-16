from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class PlayerStatistics(BaseModel):
    """Modelo para estatísticas de um jogador"""
    passes_completed: int = Field(ge=0, description="Número de passes completos")
    shots: int = Field(ge=0, description="Número total de chutes")
    goals: int = Field(ge=0, description="Número de gols marcados")
    tackles: int = Field(ge=0, description="Número de desarmes")
    interceptions: int = Field(ge=0, description="Número de interceptações")

class PlayerProfile(BaseModel):
    """Modelo para o perfil completo de um jogador"""
    player_id: int = Field(..., description="ID único do jogador")
    name: str = Field(..., description="Nome do jogador")
    team: str = Field(..., description="Nome do time do jogador")
    statistics: PlayerStatistics = Field(..., description="Estatísticas do jogador na partida")

class MatchEvent(BaseModel):
    """Modelo para eventos da partida"""
    timestamp: datetime = Field(..., description="Momento do evento")
    event_type: str = Field(..., description="Tipo do evento (gol, cartão, etc)")
    player_name: Optional[str] = Field(None, description="Nome do jogador envolvido")
    team_name: str = Field(..., description="Nome do time")
    description: str = Field(..., description="Descrição detalhada do evento")

class MatchSummary(BaseModel):
    """Modelo para o resumo da partida"""
    match_id: int = Field(..., description="ID único da partida")
    home_team: str = Field(..., description="Nome do time da casa")
    away_team: str = Field(..., description="Nome do time visitante")
    score: Dict[str, int] = Field(..., description="Placar da partida")
    key_events: List[MatchEvent] = Field(default_list, description="Eventos principais da partida")
    summary_text: str = Field(..., description="Texto descritivo do resumo da partida")

class NarrationRequest(BaseModel):
    """Modelo para requisição de narração"""
    match_id: int = Field(..., description="ID da partida")
    style: str = Field(
        ..., 
        description="Estilo da narração",
        pattern="^(formal|humoristico|tecnico)$"
    )

class NarrationResponse(BaseModel):
    """Modelo para resposta de narração"""
    match_id: int = Field(..., description="ID da partida")
    style: str = Field(..., description="Estilo usado na narração")
    narration: str = Field(..., description="Texto da narração")
    generated_at: datetime = Field(default_factory=datetime.now, description="Timestamp da geração")
