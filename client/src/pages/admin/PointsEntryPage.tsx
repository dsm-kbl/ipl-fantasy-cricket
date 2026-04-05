import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../../components/Navbar";
import apiClient from "../../api/client";
import type { MatchWithPlayers, PlayerOut } from "../../types";

/* ── Fantasy scoring rules ─────────────────────────────────── */
interface PlayerStats {
  runs: string;
  balls: string;
  fours: string;
  sixes: string;
  wickets: string;
  maidens: string;
  overs: string;
  runsConceded: string;
  catches: string;
  stumpings: string;
  runOuts: string;
  didBat: boolean;
}

const emptyStats = (): PlayerStats => ({
  runs: "", balls: "", fours: "", sixes: "",
  wickets: "", maidens: "", overs: "", runsConceded: "",
  catches: "", stumpings: "", runOuts: "",
  didBat: true,
});

function calcPoints(s: PlayerStats, role: string): number {
  const n = (v: string) => (v === "" ? 0 : Number(v));
  let pts = 0;
  const runs = n(s.runs);
  pts += runs;
  pts += n(s.fours);
  pts += n(s.sixes) * 2;
  if (runs >= 100) pts += 20;
  else if (runs >= 50) pts += 10;
  if (runs === 0 && s.didBat && n(s.balls) > 0 && role !== "BOWLER") pts -= 3;

  const wickets = n(s.wickets);
  pts += wickets * 25;
  if (wickets >= 5) pts += 20;
  else if (wickets >= 3) pts += 10;
  pts += n(s.maidens) * 8;

  const overs = n(s.overs);
  if (overs >= 2) {
    const economy = n(s.runsConceded) / overs;
    if (economy < 6) pts += 10;
    else if (economy > 12) pts -= 10;
  }

  pts += n(s.catches) * 10;
  pts += n(s.stumpings) * 10;
  pts += n(s.runOuts) * 10;
  return pts;
}

/* ── JSON parser ───────────────────────────────────────────── */

interface StatsJson {
  [playerName: string]: {
    runs?: number;
    balls?: number;
    fours?: number;
    sixes?: number;
    didBat?: boolean;
    wickets?: number;
    overs?: number;
    maidens?: number;
    runsConceded?: number;
    catches?: number;
    stumpings?: number;
    runOuts?: number;
  };
}

function normalize(name: string): string {
  return name.replace(/\s+/g, " ").trim().toLowerCase();
}

function applyJsonStats(
  json: StatsJson,
  players: PlayerOut[],
  currentStats: Record<string, PlayerStats>,
): { updated: Record<string, PlayerStats>; filled: number; unmatched: string[] } {
  const updated = { ...currentStats };
  let filled = 0;
  const unmatched: string[] = [];

  // Build a lookup: normalized JSON key → original key
  const jsonLookup = new Map<string, string>();
  for (const key of Object.keys(json)) {
    jsonLookup.set(normalize(key), key);
  }
  const matchedKeys = new Set<string>();

  for (const player of players) {
    const normalizedName = normalize(player.name);
    const jsonKey = jsonLookup.get(normalizedName);
    if (!jsonKey) continue;

    matchedKeys.add(jsonKey);

    const data = json[jsonKey];
    const s = { ...(updated[player.id] || emptyStats()) };

    const hasBatting = data.runs !== undefined || data.balls !== undefined;
    const hasBowling = data.wickets !== undefined || data.overs !== undefined;
    const hasFielding = (data.catches ?? 0) > 0 || (data.stumpings ?? 0) > 0 || (data.runOuts ?? 0) > 0;

    if (hasBatting) {
      s.runs = String(data.runs ?? 0);
      s.balls = String(data.balls ?? 0);
      s.fours = String(data.fours ?? 0);
      s.sixes = String(data.sixes ?? 0);
      s.didBat = data.didBat !== false;
      filled++;
    }
    if (data.didBat === false) {
      s.didBat = false;
      s.runs = "0"; s.balls = "0"; s.fours = "0"; s.sixes = "0";
      if (!hasBatting) filled++;
    }
    if (hasBowling) {
      s.wickets = String(data.wickets ?? 0);
      s.overs = String(data.overs ?? 0);
      s.maidens = String(data.maidens ?? 0);
      s.runsConceded = String(data.runsConceded ?? 0);
    }
    if (hasFielding) {
      s.catches = String(data.catches ?? 0);
      s.stumpings = String(data.stumpings ?? 0);
      s.runOuts = String(data.runOuts ?? 0);
    }

    updated[player.id] = s;
  }

  // Collect JSON keys that didn't match any roster player
  for (const key of Object.keys(json)) {
    if (!matchedKeys.has(key)) unmatched.push(key);
  }

  return { updated, filled, unmatched };
}
/* ── Main component ────────────────────────────────────────── */

export default function PointsEntryPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const [match, setMatch] = useState<MatchWithPlayers | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [statsMap, setStatsMap] = useState<Record<string, PlayerStats>>({});
  const [expandedPlayer, setExpandedPlayer] = useState<string | null>(null);
  const [jsonText, setJsonText] = useState("");
  const [parseMessage, setParseMessage] = useState("");

  useEffect(() => {
    if (!matchId) return;
    setLoading(true);
    apiClient
      .get<MatchWithPlayers>(`/matches/${matchId}`)
      .then((res) => {
        setMatch(res.data);
        const initial: Record<string, PlayerStats> = {};
        for (const p of res.data.players) {
          initial[p.id] = emptyStats();
        }
        setStatsMap(initial);
      })
      .catch(() => setError("Failed to load match data."))
      .finally(() => setLoading(false));
  }, [matchId]);

  const updateStat = (playerId: string, field: keyof PlayerStats, value: string | boolean) => {
    setStatsMap((prev) => ({
      ...prev,
      [playerId]: { ...prev[playerId], [field]: value },
    }));
  };

  const getPoints = (playerId: string, role: string): number => {
    const s = statsMap[playerId];
    if (!s) return 0;
    return calcPoints(s, role);
  };

  const totalPoints = match
    ? match.players.reduce((sum, p) => sum + getPoints(p.id, p.role), 0)
    : 0;

  const handleJsonParse = () => {
    if (!match || !jsonText.trim()) return;
    setParseMessage("");

    let json: StatsJson;
    try {
      json = JSON.parse(jsonText.trim());
    } catch {
      setParseMessage("Invalid JSON. Check the format and try again.");
      return;
    }

    const { updated, filled, unmatched } = applyJsonStats(json, match.players, statsMap);
    setStatsMap(updated);

    if (filled === 0) {
      setParseMessage("No players matched. Names in JSON must exactly match your roster.");
    } else if (unmatched.length > 0) {
      setParseMessage(`Filled ${filled} player(s). Unmatched names: ${unmatched.join(", ")}`);
    } else {
      setParseMessage(`Filled all ${filled} player(s). Review and submit.`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!matchId || !match) return;
    setError("");
    setSuccess("");
    setSubmitting(true);

    const points = match.players.map((p) => ({
      player_id: p.id,
      points: getPoints(p.id, p.role),
    }));

    try {
      await apiClient.post(`/admin/matches/${matchId}/points`, { points });
      setSuccess("Points submitted successfully.");
    } catch {
      try {
        await apiClient.put(`/admin/matches/${matchId}/points`, { points });
        setSuccess("Points updated successfully.");
      } catch {
        setError("Failed to save points.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50"><Navbar />
        <div className="max-w-5xl mx-auto px-4 py-8"><p className="text-gray-500">Loading match data…</p></div>
      </div>
    );
  }

  if (error && !match) {
    return (
      <div className="min-h-screen bg-gray-50"><Navbar />
        <div className="max-w-5xl mx-auto px-4 py-8">
          <p className="text-red-600">{error}</p>
          <Link to="/admin/matches" className="text-blue-600 hover:underline text-sm mt-2 inline-block">← Back to matches</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Link to="/admin/matches" className="text-blue-600 hover:underline text-sm mb-4 inline-block">← Back to matches</Link>

        {match && (
          <>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Points Entry: {match.match.team_a} vs {match.match.team_b}
            </h1>
            <p className="text-sm text-gray-500 mb-6">
              {new Date(match.match.start_time).toLocaleString()} · {match.match.venue}
            </p>

            {error && <p className="text-red-600 mb-4">{error}</p>}
            {success && <p className="text-green-600 mb-4">{success}</p>}

            {/* JSON paste section */}
            <div className="bg-white rounded-lg shadow p-4 mb-6 border border-gray-200">
              <h3 className="text-sm font-semibold text-gray-800 mb-2">📋 Paste Scorecard JSON</h3>
              <p className="text-xs text-gray-500 mb-3">
                Use ChatGPT or any LLM to convert the Cricinfo scorecard into JSON, then paste it here.
                Stats will auto-fill and fantasy points will be calculated.
              </p>
              <textarea
                value={jsonText}
                onChange={(e) => setJsonText(e.target.value)}
                placeholder='{"Virat Kohli": {"runs": 69, "balls": 38, "fours": 5, "sixes": 5}, ...}'
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm h-40 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="flex items-center gap-3 mt-2">
                <button
                  type="button"
                  onClick={handleJsonParse}
                  disabled={!jsonText.trim()}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm disabled:opacity-50 font-medium"
                >
                  Auto-fill Stats
                </button>
                {parseMessage && (
                  <p className={`text-sm ${parseMessage.includes("Invalid") || parseMessage.includes("No players") ? "text-red-600" : parseMessage.includes("didn't match") ? "text-amber-600" : "text-green-600"}`}>
                    {parseMessage}
                  </p>
                )}
              </div>
            </div>

            {/* Points guide */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="text-sm font-semibold text-blue-800 mb-1">Scoring Rules</h3>
              <div className="text-xs text-blue-700 grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-1">
                <span>1pt/run, +1/four, +2/six</span>
                <span>+10 for 50, +20 for 100</span>
                <span>-3 duck (non-bowler)</span>
                <span>25/wicket, +10 for 3W, +20 for 5W</span>
                <span>8/maiden, econ bonus/penalty</span>
                <span>10/catch, 10/stumping, 10/run-out</span>
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              <TeamSection
                label={match.match.team_a}
                players={match.players.filter((p) => p.franchise === match.match.team_a)}
                statsMap={statsMap} expandedPlayer={expandedPlayer}
                setExpandedPlayer={setExpandedPlayer} updateStat={updateStat} getPoints={getPoints}
              />
              <TeamSection
                label={match.match.team_b}
                players={match.players.filter((p) => p.franchise === match.match.team_b)}
                statsMap={statsMap} expandedPlayer={expandedPlayer}
                setExpandedPlayer={setExpandedPlayer} updateStat={updateStat} getPoints={getPoints}
              />

              <div className="flex items-center justify-between mt-6">
                <p className="text-sm text-gray-600">Total: <span className="font-bold">{totalPoints} pts</span></p>
                <button type="submit" disabled={submitting}
                  className="px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm disabled:opacity-50 font-semibold">
                  {submitting ? "Submitting…" : "Submit All Points"}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

/* ── Team section ──────────────────────────────────────────── */

function TeamSection({
  label, players, statsMap, expandedPlayer, setExpandedPlayer, updateStat, getPoints,
}: Readonly<{
  label: string;
  players: PlayerOut[];
  statsMap: Record<string, PlayerStats>;
  expandedPlayer: string | null;
  setExpandedPlayer: (id: string | null) => void;
  updateStat: (id: string, field: keyof PlayerStats, value: string | boolean) => void;
  getPoints: (id: string, role: string) => number;
}>) {
  const ptsColor = (pts: number) => pts > 0 ? "text-green-600" : pts < 0 ? "text-red-600" : "text-gray-400";

  return (
    <div className="mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-3">{label}</h2>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {players.map((p) => {
          const isExpanded = expandedPlayer === p.id;
          const pts = getPoints(p.id, p.role);
          const stats = statsMap[p.id];
          const hasSomeData = stats && (stats.runs !== "" || stats.wickets !== "" || stats.catches !== "");
          return (
            <div key={p.id} className="border-b last:border-b-0">
              <button type="button" onClick={() => setExpandedPlayer(isExpanded ? null : p.id)}
                className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 text-left">
                <div className="flex items-center gap-3">
                  {hasSomeData && <span className="w-2 h-2 rounded-full bg-green-400" />}
                  <span className="text-sm font-medium text-gray-900">{p.name}</span>
                  <span className="text-xs text-gray-500 capitalize">{p.role.replace("_", " ").toLowerCase()}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-sm font-bold ${ptsColor(pts)}`}>{pts} pts</span>
                  <svg className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                    fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {isExpanded && stats && (
                <div className="px-4 pb-4 bg-gray-50 border-t">
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 pt-3">
                    <div className="col-span-full text-xs font-semibold text-gray-500 uppercase tracking-wide pt-1">Batting</div>
                    <StatInput label="Runs" value={stats.runs} onChange={(v) => updateStat(p.id, "runs", v)} />
                    <StatInput label="Balls" value={stats.balls} onChange={(v) => updateStat(p.id, "balls", v)} />
                    <StatInput label="Fours" value={stats.fours} onChange={(v) => updateStat(p.id, "fours", v)} />
                    <StatInput label="Sixes" value={stats.sixes} onChange={(v) => updateStat(p.id, "sixes", v)} />
                    <div className="flex items-center gap-2">
                      <input type="checkbox" id={`didBat-${p.id}`} checked={stats.didBat}
                        onChange={(e) => updateStat(p.id, "didBat", e.target.checked)} className="rounded" />
                      <label htmlFor={`didBat-${p.id}`} className="text-xs text-gray-600">Did bat</label>
                    </div>
                    <div className="col-span-full text-xs font-semibold text-gray-500 uppercase tracking-wide pt-2">Bowling</div>
                    <StatInput label="Wickets" value={stats.wickets} onChange={(v) => updateStat(p.id, "wickets", v)} />
                    <StatInput label="Overs" value={stats.overs} onChange={(v) => updateStat(p.id, "overs", v)} step="0.1" />
                    <StatInput label="Runs Conceded" value={stats.runsConceded} onChange={(v) => updateStat(p.id, "runsConceded", v)} />
                    <StatInput label="Maidens" value={stats.maidens} onChange={(v) => updateStat(p.id, "maidens", v)} />
                    <div className="col-span-full text-xs font-semibold text-gray-500 uppercase tracking-wide pt-2">Fielding</div>
                    <StatInput label="Catches" value={stats.catches} onChange={(v) => updateStat(p.id, "catches", v)} />
                    <StatInput label="Stumpings" value={stats.stumpings} onChange={(v) => updateStat(p.id, "stumpings", v)} />
                    <StatInput label="Run Outs" value={stats.runOuts} onChange={(v) => updateStat(p.id, "runOuts", v)} />
                  </div>
                  <div className="mt-3 pt-3 border-t text-right">
                    <span className="text-sm text-gray-600">Calculated: </span>
                    <span className={`text-sm font-bold ${ptsColor(pts)}`}>{pts} fantasy points</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function StatInput({ label, value, onChange, step = "1" }: Readonly<{
  label: string; value: string; onChange: (v: string) => void; step?: string;
}>) {
  return (
    <div>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <input type="number" min="0" step={step} value={value}
        onChange={(e) => onChange(e.target.value)} placeholder="0"
        className="w-full border rounded px-2 py-1.5 text-sm" />
    </div>
  );
}
