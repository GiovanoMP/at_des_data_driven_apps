from pydantic import BaseModel
from typing import List, Dict, Optional

class MatchSummary(BaseModel):
    match_id: str
    home_team: str
    away_team: str
    score: Dict[str, int]
    key_events: List[Dict[str, str]]
    summary_text: str
