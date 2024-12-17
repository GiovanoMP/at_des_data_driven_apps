from pydantic import BaseModel
from typing import List, Optional

class MatchNarrative(BaseModel):
    match_id: str
    style: str
    narrative_text: str
    highlights: List[str]
