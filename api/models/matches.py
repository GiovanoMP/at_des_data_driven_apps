from pydantic import BaseModel
from typing import Optional
from datetime import datetime, time

class MatchSummary(BaseModel):
    match_id: int
    match_date: str
    kick_off: str
    competition: str
    season: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    match_status: str
    match_status_360: str
    match_week: Optional[int]
    competition_stage: str
    stadium: str
    referee: str
    home_managers: str
    away_managers: str
    data_version: str
    shot_fidelity_version: Optional[str]
    xy_fidelity_version: Optional[str]

class PlayerPosition(BaseModel):
    position_id: int
    position: str
    from_time: str
    to: Optional[str]
    from_period: int
    to_period: Optional[int]
    start_reason: str
    end_reason: str

class Player(BaseModel):
    player_id: int
    player_name: str
    player_nickname: Optional[str]
    jersey_number: int
    country: str
    cards: list
    positions: list[PlayerPosition]

class Competition(BaseModel):
    competition_id: int
    season_id: int
    country_name: str
    competition_name: str
    competition_gender: str
    competition_youth: bool
    competition_international: bool
    season_name: str
    match_updated: str
    match_updated_360: Optional[str]
    match_available_360: Optional[str]
    match_available: str
