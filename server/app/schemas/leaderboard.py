from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    total_points: float
    matches_played: int
