import { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import PlayerAvatar from "../components/PlayerAvatar";
import apiClient from "../api/client";
import type { MatchWithPlayers, PlayerOut, FantasyTeamOut } from "../types";

const TOTAL_BUDGET = 100;
const MAX_PLAYERS = 11;

const ROLE_MINIMUMS: Record<string, number> = {
  WICKET_KEEPER: 1,
  BATSMAN: 4,
  BOWLER: 3,
  ALL_ROUNDER: 1,
};

const ROLE_LABELS: Record<string, string> = {
  WICKET_KEEPER: "WK",
  BATSMAN: "BAT",
  BOWLER: "BOWL",
  ALL_ROUNDER: "AR",
};

function isLockedOut(startTime: string): boolean {
  const lockout = new Date(startTime).getTime() - 60 * 60 * 1000;
  return Date.now() >= lockout;
}

/* ── Team Column (left or right — one franchise) ────────────── */
function TeamColumn({
  teamName,
  players,
  selectedIds,
  remaining,
  locked,
  teamFull,
  onAdd,
  color,
}: Readonly<{
  teamName: string;
  players: PlayerOut[];
  selectedIds: Set<string>;
  remaining: number;
  locked: boolean;
  teamFull: boolean;
  onAdd: (p: PlayerOut) => void;
  color: string;
}>) {
  const [roleFilter, setRoleFilter] = useState<string>("ALL");

  const filtered = useMemo(() => {
    return players.filter((p) => {
      if (roleFilter === "OVERSEAS") return p.nationality && p.nationality !== "India";
      if (roleFilter === "INDIAN") return !p.nationality || p.nationality === "India";
      if (roleFilter !== "ALL") return p.role === roleFilter;
      return true;
    });
  }, [players, roleFilter]);

  return (
    <div className="flex flex-col h-full">
      <div className={`px-3 py-2 ${color} rounded-t-lg`}>
        <h3 className="text-sm font-bold text-white text-center truncate">{teamName}</h3>
        <p className="text-xs text-white/70 text-center">{players.length} players</p>
      </div>
      <div className="flex gap-1 p-2 bg-white border-x border-gray-200 flex-wrap justify-center">
        {["ALL", ...Object.keys(ROLE_LABELS), "OVERSEAS", "INDIAN"].map((r) => (
          <button
            key={r}
            onClick={() => setRoleFilter(r)}
            className={`px-2 py-0.5 text-xs rounded font-medium ${
              roleFilter === r ? "bg-gray-800 text-white" : "bg-gray-100 text-gray-500 hover:bg-gray-200"
            }`}
          >
            {r === "ALL" ? "All" : r === "OVERSEAS" ? "✈️ OS" : r === "INDIAN" ? "🇮🇳" : ROLE_LABELS[r]}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto bg-white border-x border-b border-gray-200 rounded-b-lg divide-y divide-gray-100">
        {filtered.map((player) => {
          const selected = selectedIds.has(player.id);
          const tooExpensive = player.cost > remaining;
          const disabled = locked || selected || teamFull || tooExpensive;

          return (
            <button
              key={player.id}
              onClick={() => !disabled && onAdd(player)}
              disabled={disabled}
              className={`w-full flex items-center gap-2 px-3 py-2 text-left transition ${
                selected
                  ? "bg-blue-50 opacity-50"
                  : disabled
                  ? "opacity-40 cursor-not-allowed"
                  : "hover:bg-gray-50 cursor-pointer"
              }`}
            >
              <PlayerAvatar player={player} size={32} />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-gray-900 truncate">
                  {player.name}
                  {player.nationality && player.nationality !== "India" && (
                    <span className="ml-1" title={`Overseas (${player.nationality})`}>✈️</span>
                  )}
                </p>
                <p className="text-[10px] text-gray-400">{ROLE_LABELS[player.role] || player.role}</p>
              </div>
              <span className="text-xs font-bold text-gray-600 shrink-0">{player.cost}</span>
              {selected && <span className="text-[10px] text-blue-600 font-medium">✓</span>}
            </button>
          );
        })}
        {filtered.length === 0 && (
          <p className="px-3 py-6 text-center text-gray-400 text-xs">No players</p>
        )}
      </div>
    </div>
  );
}

/* ── Your XI (center panel) ─────────────────────────────────── */
function YourXI({
  players,
  locked,
  remaining,
  rolesValid,
  submitting,
  existingTeam,
  onRemove,
  onSubmit,
  onDelete,
  warningMsg,
  successMsg,
  teamA,
  teamB,
  allPlayers,
  tossPrediction,
  setTossPrediction,
  motmPrediction,
  setMotmPrediction,
}: Readonly<{
  players: PlayerOut[];
  locked: boolean;
  remaining: number;
  rolesValid: boolean;
  submitting: boolean;
  existingTeam: FantasyTeamOut | null;
  onRemove: (p: PlayerOut) => void;
  onSubmit: () => void;
  onDelete: () => void;
  warningMsg: string;
  successMsg: string;
  teamA: string;
  teamB: string;
  allPlayers: PlayerOut[];
  tossPrediction: string;
  setTossPrediction: (v: string) => void;
  motmPrediction: string;
  setMotmPrediction: (v: string) => void;
}>) {
  const counts: Record<string, number> = {};
  for (const p of players) {
    counts[p.role] = (counts[p.role] || 0) + 1;
  }
  const overseasCount = players.filter((p) => p.nationality && p.nationality !== "India").length;

  const pct = Math.max(0, Math.min(100, (remaining / TOTAL_BUDGET) * 100));
  let barColor = "bg-green-500";
  if (remaining < 10) barColor = "bg-red-500";
  else if (remaining < 30) barColor = "bg-yellow-400";

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 rounded-t-lg">
        <h3 className="text-sm font-bold text-white text-center">
          Your XI ({players.length}/{MAX_PLAYERS})
        </h3>
        <div className="mt-2">
          <div className="flex justify-between text-[10px] text-blue-100 mb-1">
            <span>Budget</span>
            <span className="font-bold">{remaining.toFixed(1)} / {TOTAL_BUDGET}</span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-1.5">
            <div className={`h-1.5 rounded-full transition-all ${barColor}`} style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>

      {/* Role badges */}
      <div className="flex gap-1 p-2 bg-white border-x border-gray-200 justify-center flex-wrap">
        {Object.entries(ROLE_MINIMUMS).map(([role, min]) => {
          const count = counts[role] || 0;
          const met = count >= min;
          return (
            <span
              key={role}
              className={`px-2 py-0.5 text-[10px] rounded font-semibold ${
                met ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
              }`}
            >
              {ROLE_LABELS[role]} {count}/{min}
            </span>
          );
        })}
        <span
          className={`px-2 py-0.5 text-[10px] rounded font-semibold ${
            overseasCount <= 4 ? "bg-blue-100 text-blue-700" : "bg-red-100 text-red-600"
          }`}
        >
          ✈️ {overseasCount}/4
        </span>
      </div>

      {/* Messages */}
      {warningMsg && (
        <div className="mx-2 mt-2 p-2 bg-red-50 border border-red-200 text-red-700 rounded text-xs">
          {warningMsg}
        </div>
      )}
      {successMsg && (
        <div className="mx-2 mt-2 p-2 bg-green-50 border border-green-200 text-green-700 rounded text-xs">
          {successMsg}
        </div>
      )}

      {/* Predictions */}
      {!locked && (
        <div className="px-3 py-2 bg-gray-50 border-x border-gray-200 space-y-2">
          <p className="text-[10px] font-semibold text-gray-500 uppercase tracking-wide">Bonus Predictions</p>
          <div className="flex gap-2">
            <div className="flex-1">
              <label className="text-[10px] text-gray-500 block mb-0.5">🪙 Toss Winner</label>
              <select
                value={tossPrediction}
                onChange={(e) => setTossPrediction(e.target.value)}
                className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select team</option>
                <option value={teamA}>{teamA}</option>
                <option value={teamB}>{teamB}</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="text-[10px] text-gray-500 block mb-0.5">⭐ Man of the Match</label>
              <select
                value={motmPrediction}
                onChange={(e) => setMotmPrediction(e.target.value)}
                className="w-full text-xs border border-gray-300 rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">Select player</option>
                {allPlayers.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
          </div>
          <p className="text-[10px] text-gray-400">+10 pts for correct toss · +25 pts for correct MOTM</p>
        </div>
      )}

      {/* Player list */}
      <div className="flex-1 overflow-y-auto bg-white border-x border-gray-200 divide-y divide-gray-100">
        {players.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-300 py-12">
            <span className="text-3xl mb-2">🏏</span>
            <p className="text-xs">Pick players from both teams</p>
          </div>
        ) : (
          players.map((player) => (
            <div key={player.id} className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50">
              <PlayerAvatar player={player} size={30} />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-gray-900 truncate">
                  {player.name}
                  {player.nationality && player.nationality !== "India" && (
                    <span className="ml-1" title={`Overseas (${player.nationality})`}>✈️</span>
                  )}
                </p>
                <p className="text-[10px] text-gray-400">
                  {ROLE_LABELS[player.role]} · {player.cost} cr
                </p>
              </div>
              {!locked && (
                <button
                  onClick={() => onRemove(player)}
                  className="shrink-0 w-5 h-5 flex items-center justify-center rounded-full bg-red-100 text-red-500 hover:bg-red-200 text-xs"
                >
                  ×
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {/* Action buttons */}
      {!locked && (
        <div className="p-2 bg-white border-x border-b border-gray-200 rounded-b-lg space-y-2">
          <button
            onClick={onSubmit}
            disabled={submitting || players.length !== MAX_PLAYERS || !rolesValid}
            className={`w-full py-2 text-xs font-semibold rounded-lg transition ${
              players.length !== MAX_PLAYERS || submitting || !rolesValid
                ? "bg-gray-200 text-gray-400 cursor-not-allowed"
                : "bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700 shadow"
            }`}
          >
            {submitting ? "Saving…" : existingTeam ? "Update Team" : "Save Team"}
          </button>
          {existingTeam && (
            <button
              onClick={onDelete}
              disabled={submitting}
              className="w-full py-1.5 text-xs font-medium rounded-lg border border-red-200 text-red-500 hover:bg-red-50 disabled:opacity-50"
            >
              Delete Team
            </button>
          )}
        </div>
      )}
      {locked && (
        <div className="p-3 bg-yellow-50 border-x border-b border-yellow-200 rounded-b-lg text-center">
          <p className="text-xs text-yellow-700 font-medium">🔒 Team locked</p>
        </div>
      )}
    </div>
  );
}


/* ── Mobile Tab Selector ────────────────────────────────────── */
type MobileTab = "teamA" | "yourXI" | "teamB";

/* ── Main Page Component ────────────────────────────────────── */
export default function TeamBuilderPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const navigate = useNavigate();

  const [matchData, setMatchData] = useState<MatchWithPlayers | null>(null);
  const [existingTeam, setExistingTeam] = useState<FantasyTeamOut | null>(null);
  const [selectedPlayers, setSelectedPlayers] = useState<PlayerOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [warningMsg, setWarningMsg] = useState("");
  const [mobileTab, setMobileTab] = useState<MobileTab>("teamA");
  const [tossPrediction, setTossPrediction] = useState<string>("");
  const [motmPrediction, setMotmPrediction] = useState<string>("");

  useEffect(() => {
    if (!matchId) return;
    const fetchData = async () => {
      try {
        const [matchRes, teamRes] = await Promise.allSettled([
          apiClient.get<MatchWithPlayers>(`/matches/${matchId}`),
          apiClient.get<FantasyTeamOut>(`/fantasy-teams/${matchId}`),
        ]);
        if (matchRes.status === "fulfilled") {
          setMatchData(matchRes.value.data);
        } else {
          setError("Failed to load match data.");
          return;
        }
        if (teamRes.status === "fulfilled") {
          const team = teamRes.value.data;
          setExistingTeam(team);
          setSelectedPlayers(team.players);
          if (team.toss_prediction) setTossPrediction(team.toss_prediction);
          if (team.motm_prediction) setMotmPrediction(team.motm_prediction);
        }
      } catch {
        setError("Failed to load data.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [matchId]);

  const selectedIds = useMemo(() => new Set(selectedPlayers.map((p) => p.id)), [selectedPlayers]);
  const totalCost = useMemo(() => selectedPlayers.reduce((sum, p) => sum + p.cost, 0), [selectedPlayers]);
  const remaining = TOTAL_BUDGET - totalCost;
  const teamFull = selectedPlayers.length >= MAX_PLAYERS;
  const locked = matchData ? isLockedOut(matchData.match.start_time) : false;

  const rolesValid = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const p of selectedPlayers) {
      counts[p.role] = (counts[p.role] || 0) + 1;
    }
    return Object.entries(ROLE_MINIMUMS).every(([role, min]) => (counts[role] || 0) >= min);
  }, [selectedPlayers]);

  const handleAdd = (player: PlayerOut) => {
    setSuccessMsg("");
    if (locked || selectedIds.has(player.id)) return;
    if (teamFull) {
      setWarningMsg("Team is full — you already have 11 players.");
      return;
    }
    if (player.cost > remaining) {
      setWarningMsg(`Insufficient budget. ${player.name} costs ${player.cost} cr but you only have ${remaining.toFixed(1)} cr left.`);
      return;
    }
    setWarningMsg("");
    setSelectedPlayers((prev) => [...prev, player]);
  };

  const handleRemove = (player: PlayerOut) => {
    setSuccessMsg("");
    setWarningMsg("");
    if (locked) return;
    setSelectedPlayers((prev) => prev.filter((p) => p.id !== player.id));
  };

  const handleSubmit = async () => {
    if (!matchId || locked) return;
    setWarningMsg("");
    setSuccessMsg("");
    if (selectedPlayers.length !== MAX_PLAYERS) {
      setWarningMsg(`You need exactly ${MAX_PLAYERS} players. Currently selected: ${selectedPlayers.length}.`);
      return;
    }
    if (!rolesValid) {
      setWarningMsg("Role requirements not met. You need at least 1 WK, 4 BAT, 3 BOWL, and 1 AR.");
      return;
    }
    const playerIds = selectedPlayers.map((p) => p.id);
    setSubmitting(true);
    try {
      if (existingTeam) {
        const res = await apiClient.put<FantasyTeamOut>(`/fantasy-teams/${existingTeam.id}`, {
          player_ids: playerIds,
          toss_prediction: tossPrediction || null,
          motm_prediction: motmPrediction || null,
        });
        setExistingTeam(res.data);
        setSuccessMsg("Team updated successfully!");
      } else {
        const res = await apiClient.post<FantasyTeamOut>("/fantasy-teams", {
          match_id: matchId,
          player_ids: playerIds,
          toss_prediction: tossPrediction || null,
          motm_prediction: motmPrediction || null,
        });
        setExistingTeam(res.data);
        setSuccessMsg("Team saved successfully!");
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { error?: { message?: string } } } };
      setWarningMsg(axiosErr?.response?.data?.error?.message || "Failed to save team.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!existingTeam || locked) return;
    setWarningMsg("");
    setSuccessMsg("");
    setSubmitting(true);
    try {
      await apiClient.delete(`/fantasy-teams/${existingTeam.id}`);
      setExistingTeam(null);
      setSelectedPlayers([]);
      setSuccessMsg("Team deleted.");
    } catch {
      setWarningMsg("Failed to delete team.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <p className="text-center text-gray-500 mt-12">Loading team builder…</p>
      </div>
    );
  }

  if (error || !matchData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600">{error || "Match not found."}</p>
          <button onClick={() => navigate("/matches")} className="mt-4 text-blue-600 hover:underline text-sm">
            ← Back to matches
          </button>
        </div>
      </div>
    );
  }

  const { match, players } = matchData;
  const date = new Date(match.start_time);
  const teamAPlayers = players.filter((p) => p.franchise === match.team_a);
  const teamBPlayers = players.filter((p) => p.franchise === match.team_b);

  const sharedProps = {
    selectedIds,
    remaining,
    locked,
    teamFull,
    onAdd: handleAdd,
  };

  const yourXIProps = {
    players: selectedPlayers,
    locked,
    remaining,
    rolesValid,
    submitting,
    existingTeam,
    onRemove: handleRemove,
    onSubmit: handleSubmit,
    onDelete: handleDelete,
    warningMsg,
    successMsg,
    teamA: match.team_a,
    teamB: match.team_b,
    allPlayers: players,
    tossPrediction,
    setTossPrediction,
    motmPrediction,
    setMotmPrediction,
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navbar />

      {/* Match header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <button onClick={() => navigate(`/matches/${matchId}`)} className="text-blue-200 hover:text-white text-sm">
            ← Back
          </button>
          <div className="text-center">
            <h1 className="text-lg font-bold">{match.team_a} vs {match.team_b}</h1>
            <p className="text-xs text-blue-200">
              {date.toLocaleDateString()} · {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} · {match.venue}
            </p>
          </div>
          <span className="text-xs px-2 py-1 rounded bg-white/20">{match.status}</span>
        </div>
      </div>

      {/* Mobile tabs (visible on small screens) */}
      <div className="lg:hidden flex border-b border-gray-300 bg-white sticky top-0 z-10">
        {([
          ["teamA", match.team_a],
          ["yourXI", `Your XI (${selectedPlayers.length})`],
          ["teamB", match.team_b],
        ] as [MobileTab, string][]).map(([tab, label]) => (
          <button
            key={tab}
            onClick={() => setMobileTab(tab)}
            className={`flex-1 py-3 text-xs font-semibold text-center transition ${
              mobileTab === tab
                ? "text-blue-600 border-b-2 border-blue-600 bg-blue-50"
                : "text-gray-500"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Desktop: 3-column layout */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        {/* Desktop */}
        <div className="hidden lg:grid lg:grid-cols-[1fr_1.2fr_1fr] gap-4" style={{ height: "calc(100vh - 140px)" }}>
          <TeamColumn
            teamName={match.team_a}
            players={teamAPlayers}
            color="bg-blue-700"
            {...sharedProps}
          />
          <YourXI {...yourXIProps} />
          <TeamColumn
            teamName={match.team_b}
            players={teamBPlayers}
            color="bg-red-700"
            {...sharedProps}
          />
        </div>

        {/* Mobile */}
        <div className="lg:hidden" style={{ height: "calc(100vh - 180px)" }}>
          {mobileTab === "teamA" && (
            <TeamColumn
              teamName={match.team_a}
              players={teamAPlayers}
              color="bg-blue-700"
              {...sharedProps}
            />
          )}
          {mobileTab === "yourXI" && <YourXI {...yourXIProps} />}
          {mobileTab === "teamB" && (
            <TeamColumn
              teamName={match.team_b}
              players={teamBPlayers}
              color="bg-red-700"
              {...sharedProps}
            />
          )}
        </div>
      </div>
    </div>
  );
}
