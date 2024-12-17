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

class PlayerPosition(BaseModel):
    """Modelo para posição do jogador durante a partida"""
    position_id: int = Field(..., description="ID da posição")
    position: str = Field(..., description="Nome da posição")
    from_time: str = Field(..., alias="from", description="Momento de início")
    to_time: Optional[str] = Field(None, alias="to", description="Momento de fim")
    from_period: int = Field(..., description="Período de início")
    to_period: Optional[int] = Field(None, description="Período de fim")
    start_reason: str = Field(..., description="Razão da entrada")
    end_reason: Optional[str] = Field(None, description="Razão da saída")

class PlayerProfile(BaseModel):
    """Modelo para o perfil do jogador baseado nos dados reais da StatsBomb"""
    player_id: int = Field(..., description="ID único do jogador")
    player_name: str = Field(..., description="Nome completo do jogador")
    player_nickname: Optional[str] = Field(None, description="Apelido do jogador")
    jersey_number: int = Field(..., description="Número da camisa")
    country: Optional[str] = Field(None, description="País do jogador")
    cards: List[str] = Field(default_factory=list, description="Cartões recebidos")
    positions: List[PlayerPosition] = Field(..., description="Posições ocupadas durante a partida")
    statistics: PlayerStatistics = Field(..., description="Estatísticas do jogador na partida")

class MatchEvent(BaseModel):
    """Modelo para eventos da partida baseado nos dados reais da StatsBomb"""
    id: int = Field(..., description="ID único do evento")
    index: int = Field(..., description="Índice do evento na sequência da partida")
    period: int = Field(..., description="Período do jogo")
    timestamp: str = Field(..., description="Momento do evento")
    minute: int = Field(..., description="Minuto do jogo")
    second: int = Field(..., description="Segundo do jogo")
    type: Dict[str, str] = Field(..., description="Tipo e subtipo do evento")
    possession: int = Field(..., description="Número da posse de bola")
    possession_team: Dict[str, str] = Field(..., description="Time com a posse de bola")
    play_pattern: Dict[str, str] = Field(..., description="Padrão de jogo")
    team: Dict[str, str] = Field(..., description="Time que realizou o evento")
    player: Optional[Dict[str, str]] = Field(None, description="Jogador que realizou o evento")
    position: Optional[Dict[str, str]] = Field(None, description="Posição do jogador")
    location: Optional[List[float]] = Field(None, description="Coordenadas [x, y] do evento")
    duration: Optional[float] = Field(None, description="Duração do evento em segundos")
    under_pressure: Optional[bool] = Field(None, description="Indica se o jogador estava sob pressão")
    related_events: Optional[List[int]] = Field(None, description="IDs de eventos relacionados")

class MatchSummary(BaseModel):
    """Modelo para o resumo da partida baseado nos dados reais da StatsBomb"""
    match_id: int = Field(..., description="ID único da partida")
    match_date: str = Field(..., description="Data da partida")
    kick_off: str = Field(..., description="Horário de início da partida")
    competition: str = Field(..., description="Nome da competição")
    season: str = Field(..., description="Temporada")
    home_team: str = Field(..., description="Time mandante")
    away_team: str = Field(..., description="Time visitante")
    home_score: int = Field(..., description="Gols do time mandante")
    away_score: int = Field(..., description="Gols do time visitante")
    match_status: str = Field(..., description="Status da partida")
    match_status_360: str = Field(..., description="Status dos dados 360")
    competition_stage: str = Field(..., description="Fase da competição")
    stadium: Optional[str] = Field(None, description="Estádio onde a partida foi realizada")
    referee: Optional[str] = Field(None, description="Árbitro da partida")
    home_managers: Optional[str] = Field(None, description="Técnico do time mandante")
    away_managers: Optional[str] = Field(None, description="Técnico do time visitante")
    data_version: str = Field(..., description="Versão dos dados")
    shot_fidelity_version: Optional[str] = Field(None, description="Versão dos dados de chutes")
    xy_fidelity_version: Optional[str] = Field(None, description="Versão dos dados de posicionamento")

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
