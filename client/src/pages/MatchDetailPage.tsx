import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import PageBackground from "../components/PageBackground";
import PlayerAvatar from "../components/PlayerAvatar";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import type { MatchWithPlayers } from "../types";

export default function MatchDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState<MatchWithPlayers | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    apiClient
      .get<MatchWithPlayers>(`/matches/${id}`)
      .then((res) => setData(res.data))
      .catch(() => setError("Failed to load match details."))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <PageBackground>
        <Navbar />
        <div className="text-center py-16">
          <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
        </div>
      </PageBackground>
    );
  }

  if (error || !data) {
    return (
      <PageBackground>
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600 bg-red-50 p-4 rounded-xl">{error || "Match not found."}</p>
          <button onClick={() => navigate("/matches")} className="mt-4 text-blue-600 hover:underline text-sm">← Back to matches</button>
        </div>
      </PageBackground>
    );
  }

  const { match, players } = data;
  const date = new Date(match.start_time);

  return (
    <PageBackground>
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">

        {/* Match header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-lg p-6 mb-6 text-white">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-2xl font-extrabold">{match.team_a} vs {match.team_b}</h1>
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-white/20">{match.status}</span>
          </div>
          <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-sm text-blue-200">
            <span>📅 {date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}</span>
            <span>🕐 {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
            <span>📍 {match.venue}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900">Player Pool ({players.length})</h2>
          {!isAdmin && (
            <Link
              to={`/team-builder/${match.id}`}
              className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm font-semibold rounded-xl hover:from-blue-700 hover:to-indigo-700 shadow transition"
            >
              Build Team
            </Link>
          )}
        </div>

        {/* Player pool - cards on mobile, table on desktop */}
        <div className="bg-white/80 backdrop-blur rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          {/* Desktop table */}
          <table className="w-full text-sm hidden md:table">
            <thead className="bg-gray-50 text-gray-500">
              <tr>
                <th className="text-left px-5 py-3 font-medium">Name</th>
                <th className="text-left px-5 py-3 font-medium">Role</th>
                <th className="text-left px-5 py-3 font-medium">Franchise</th>
                <th className="text-right px-5 py-3 font-medium">Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {players.map((player) => (
                <tr key={player.id} className="hover:bg-blue-50/30 transition">
                  <td className="px-5 py-3 text-gray-900">
                    <div className="flex items-center gap-2.5">
                      <PlayerAvatar player={player} size={30} />
                      <span className="font-medium">{player.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3 text-gray-500">{player.role}</td>
                  <td className="px-5 py-3 text-gray-500">{player.franchise}</td>
                  <td className="px-5 py-3 text-right font-semibold text-gray-900">{player.cost} cr</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Mobile cards */}
          <div className="md:hidden divide-y divide-gray-100">
            {players.map((player) => (
              <div key={player.id} className="flex items-center gap-3 px-4 py-3">
                <PlayerAvatar player={player} size={36} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{player.name}</p>
                  <p className="text-xs text-gray-400">{player.role} · {player.franchise}</p>
                </div>
                <span className="text-sm font-bold text-gray-700 shrink-0">{player.cost} cr</span>
              </div>
            ))}
          </div>

          {players.length === 0 && (
            <p className="px-5 py-8 text-center text-gray-400">No players in the pool.</p>
          )}
        </div>

        <button onClick={() => navigate("/matches")} className="mt-6 text-blue-600 hover:underline text-sm">← Back to matches</button>
      </div>
    </PageBackground>
  );
}
