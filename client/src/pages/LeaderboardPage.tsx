import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import PageBackground from "../components/PageBackground";
import apiClient from "../api/client";
import type { LeaderboardEntry, MatchOut } from "../types";

type Tab = "overall" | "per-match";
type SortBy = "total" | "avg";

export default function LeaderboardPage() {
  const [tab, setTab] = useState<Tab>("overall");
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [matches, setMatches] = useState<MatchOut[]>([]);
  const [selectedMatchId, setSelectedMatchId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sortBy, setSortBy] = useState<SortBy>("total");

  const sortedEntries = tab === "overall"
    ? [...entries].sort((a, b) =>
        sortBy === "avg"
          ? b.avg_points_per_match - a.avg_points_per_match || b.total_points - a.total_points
          : b.total_points - a.total_points || b.matches_played - a.matches_played
      ).map((e, idx) => ({ ...e, rank: idx + 1 }))
    : entries;

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

  useEffect(() => {
    if (tab !== "per-match") return;
    setEntries([]);
    setSelectedMatchId("");
    apiClient.get<MatchOut[]>("/matches/completed").then((res) => setMatches(res.data)).catch(() => {});
  }, [tab]);

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

  return (
    <PageBackground>
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-6">Leaderboard</h1>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab("overall")}
            className={`px-5 py-2 text-sm font-semibold rounded-full transition ${
              tab === "overall"
                ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow"
                : "bg-white text-gray-500 border border-gray-200 hover:border-blue-300"
            }`}
          >
            Overall
          </button>
          <button
            onClick={() => setTab("per-match")}
            className={`px-5 py-2 text-sm font-semibold rounded-full transition ${
              tab === "per-match"
                ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow"
                : "bg-white text-gray-500 border border-gray-200 hover:border-blue-300"
            }`}
          >
            Per Match
          </button>
        </div>

        {tab === "overall" && (
          <div className="flex gap-2 mb-4">
            <span className="text-xs text-gray-400 self-center mr-1">Sort by:</span>
            <button
              onClick={() => setSortBy("total")}
              className={`px-3 py-1 text-xs font-medium rounded-full transition ${
                sortBy === "total"
                  ? "bg-blue-100 text-blue-700 border border-blue-200"
                  : "bg-gray-50 text-gray-500 border border-gray-200 hover:border-blue-200"
              }`}
            >
              Total Points
            </button>
            <button
              onClick={() => setSortBy("avg")}
              className={`px-3 py-1 text-xs font-medium rounded-full transition ${
                sortBy === "avg"
                  ? "bg-blue-100 text-blue-700 border border-blue-200"
                  : "bg-gray-50 text-gray-500 border border-gray-200 hover:border-blue-200"
              }`}
            >
              Avg / Match
            </button>
          </div>
        )}

        {tab === "per-match" && (
          <div className="mb-6">
            <select
              value={selectedMatchId}
              onChange={(e) => setSelectedMatchId(e.target.value)}
              className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

        {error && <p className="text-red-600 bg-red-50 p-4 rounded-xl mb-4">{error}</p>}

        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
          </div>
        )}

        {!loading && sortedEntries.length === 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
            <span className="text-3xl">🏆</span>
            <p className="text-gray-400 mt-2 text-sm">
              {tab === "per-match" && !selectedMatchId ? "Select a match to view its leaderboard." : "No leaderboard data available."}
            </p>
          </div>
        )}

        {!loading && sortedEntries.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            {sortedEntries.map((entry, idx) => {
              let rankBg = "bg-gray-50";
              let rankText = "text-gray-600";
              if (entry.rank === 1) { rankBg = "bg-yellow-50"; rankText = "text-yellow-600"; }
              else if (entry.rank === 2) { rankBg = "bg-gray-100"; rankText = "text-gray-500"; }
              else if (entry.rank === 3) { rankBg = "bg-orange-50"; rankText = "text-orange-500"; }

              return (
                <div
                  key={entry.username}
                  className={`flex items-center justify-between px-5 py-3.5 ${idx > 0 ? "border-t border-gray-100" : ""} hover:bg-blue-50/30 transition`}
                >
                  <div className="flex items-center gap-4">
                    <span className={`w-8 h-8 rounded-full ${rankBg} ${rankText} flex items-center justify-center text-sm font-bold`}>
                      {entry.rank <= 3 ? ["🥇", "🥈", "🥉"][entry.rank - 1] : `#${entry.rank}`}
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{entry.username}</p>
                      <p className="text-[10px] text-gray-400">{entry.matches_played} match{entry.matches_played !== 1 ? "es" : ""} played</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    {tab === "overall" && (
                      <div className="text-right">
                        <p className="text-sm font-bold text-gray-500">{entry.avg_points_per_match}</p>
                        <p className="text-[10px] text-gray-400">avg/match</p>
                      </div>
                    )}
                    <div className="text-right">
                      <p className="text-lg font-extrabold text-blue-600">{entry.total_points}</p>
                      <p className="text-[10px] text-gray-400">total</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </PageBackground>
  );
}
