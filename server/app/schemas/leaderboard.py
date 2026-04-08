from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    total_points: float
    matches_played: int
    avg_points_per_match: float
