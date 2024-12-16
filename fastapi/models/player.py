from pydantic import BaseModel
from typing import Dict, List, Optional

class PlayerProfile(BaseModel):
    player_id: str
    name: str
    team: str
    position: str
    statistics: Dict[str, float]
    performance_metrics: Dict[str, float]
