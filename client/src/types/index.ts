/* Shared TypeScript types matching backend Pydantic schemas */

export interface UserOut {
  id: string;
  username: string;
  email: string;
  role: string;
  is_verified: boolean;
}

export interface AuthTokenResponse {
  user: UserOut;
  token: string;
}

export interface PlayerOut {
  id: string;
  name: string;
  role: string;
  franchise: string;
  cost: number;
  image_url: string | null;
  nationality: string | null;
}

export interface MatchOut {
  id: string;
  team_a: string;
  team_b: string;
  venue: string;
  start_time: string;
  status: string;
  toss_winner: string | null;
  motm_player_id: string | null;
}

export interface MatchWithPlayers {
  match: MatchOut;
  players: PlayerOut[];
}

export interface FantasyTeamOut {
  id: string;
  user_id: string;
  match_id: string;
  total_score: number;
  players: PlayerOut[];
  remaining_budget: number;
  toss_prediction: string | null;
  motm_prediction: string | null;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  total_points: number;
  matches_played: number;
  avg_points_per_match: number;
}

export interface PlayerPointsOut {
  player_id: string;
  player_name: string;
  franchise: string;
  role: string;
  points: number;
}

export interface MatchParticipation {
  match: MatchOut;
  team_id: string;
  total_score: number;
}

export interface UpcomingMatchStatus {
  match: MatchOut;
  status: string;
}

export interface DashboardResponse {
  participated_matches: MatchParticipation[];
  overall_rank: number | null;
  upcoming_matches: UpcomingMatchStatus[];
}

export interface MatchDetailPlayer {
  player_id: string;
  player_name: string;
  franchise: string;
  role: string;
  cost: number;
  points: number | null;
}

export interface DashboardMatchDetail {
  match: MatchOut;
  team_id: string;
  total_score: number;
  players: MatchDetailPlayer[];
}

export interface ErrorDetail {
  field: string | null;
  message: string;
}

export interface ErrorBody {
  code: string;
  message: string;
  details: ErrorDetail[];
}

export interface ErrorResponse {
  error: ErrorBody;
}
