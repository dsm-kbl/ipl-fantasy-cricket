import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import apiClient from "../api/client";
import type { LeaderboardEntry, MatchOut } from "../types";

type Tab = "overall" | "per-match";

export default function LeaderboardPage() {
  const [tab, setTab] = useState<Tab>("overall");
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [matches, setMatches] = useState<MatchOut[]>([]);
  const [selectedMatchId, setSelectedMatchId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch overall leaderboard on mount and when switching to overall tab
  useEffect(() => {
    if (tab !== "overall") return;
    setLoading(true);
    setError("");
    apiClient
      .get<LeaderboardEntry[]>("/leaderboard")
      .then((res) => setEntries(res.data))
      .catch(() => setError("Failed to load leaderboard."))
      .finally(() => setLoading(false));
  }, [tab]);

  // Fetch matches list when switching to per-match tab
  useEffect(() => {
    if (tab !== "per-match") return;
    setEntries([]);
    setSelectedMatchId("");
    apiClient
      .get<MatchOut[]>("/matches")
      .then((res) => setMatches(res.data))
      .catch(() => setError("Failed to load matches."));
  }, [tab]);

  // Fetch per-match leaderboard when a match is selected
  useEffect(() => {
    if (tab !== "per-match" || !selectedMatchId) return;
    setLoading(true);
    setError("");
    apiClient
      .get<LeaderboardEntry[]>(`/matches/${selectedMatchId}/leaderboard`)
      .then((res) => setEntries(res.data))
      .catch(() => setError("Failed to load match leaderboard."))
      .finally(() => setLoading(false));
  }, [tab, selectedMatchId]);

  const tabClass = (t: Tab) =>
    `px-4 py-2 text-sm font-medium rounded-t-lg ${
      tab === t
        ? "bg-white text-blue-600 border-b-2 border-blue-600"
        : "text-gray-500 hover:text-gray-700"
    }`;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Leaderboard</h1>

        {/* Tabs */}
        <div className="flex gap-2 mb-4 border-b border-gray-200">
          <button className={tabClass("overall")} onClick={() => setTab("overall")}>
            Overall
          </button>
          <button className={tabClass("per-match")} onClick={() => setTab("per-match")}>
            Per Match
          </button>
        </div>

        {/* Per-match selector */}
        {tab === "per-match" && (
          <div className="mb-4">
            <select
              value={selectedMatchId}
              onChange={(e) => setSelectedMatchId(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a match</option>
              {matches.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.team_a} vs {m.team_b} — {new Date(m.start_time).toLocaleDateString()}
                </option>
              ))}
            </select>
          </div>
        )}

        {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

        {loading && (
          <p className="text-center text-gray-500 mt-8">Loading…</p>
        )}

        {!loading && entries.length === 0 && (
          <div className="bg-white rounded-lg shadow p-6 text-center text-gray-400 text-sm">
            {tab === "per-match" && !selectedMatchId
              ? "Select a match to view its leaderboard."
              : "No leaderboard data available."}
          </div>
        )}

        {!loading && entries.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-100 text-gray-600 text-left">
                <tr>
                  <th className="px-4 py-3 w-16">Rank</th>
                  <th className="px-4 py-3">Username</th>
                  <th className="px-4 py-3 text-right">Total Points</th>
                  <th className="px-4 py-3 text-right">Matches Played</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {entries.map((entry) => (
                  <tr key={entry.username} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">#{entry.rank}</td>
                    <td className="px-4 py-3 text-gray-800">{entry.username}</td>
                    <td className="px-4 py-3 text-right font-semibold text-blue-600">
                      {entry.total_points}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-500">
                      {entry.matches_played}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
