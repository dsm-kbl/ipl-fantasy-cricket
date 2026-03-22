import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import PlayerAvatar from "../components/PlayerAvatar";
import apiClient from "../api/client";
import type { MatchWithPlayers } from "../types";

export default function MatchDetailPage() {
  const { id } = useParams<{ id: string }>();
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
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <p className="text-center text-gray-500 mt-12">Loading match details…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600">{error || "Match not found."}</p>
          <button onClick={() => navigate("/matches")} className="mt-4 text-blue-600 hover:underline">
            ← Back to matches
          </button>
        </div>
      </div>
    );
  }

  const { match, players } = data;
  const date = new Date(match.start_time);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Match header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h1 className="text-2xl font-bold text-gray-900">
              {match.team_a} vs {match.team_b}
            </h1>
            <span className="text-xs font-medium px-2 py-1 rounded bg-blue-100 text-blue-700">
              {match.status}
            </span>
          </div>
          <div className="text-sm text-gray-600 space-y-1">
            <p>📅 {date.toLocaleDateString()} · 🕐 {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</p>
            <p>📍 {match.venue}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Player Pool ({players.length})</h2>
          <Link
            to={`/team-builder/${match.id}`}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700"
          >
            Build Team
          </Link>
        </div>

        {/* Player pool table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-100 text-gray-700">
              <tr>
                <th className="text-left px-4 py-3 font-medium">Name</th>
                <th className="text-left px-4 py-3 font-medium">Role</th>
                <th className="text-left px-4 py-3 font-medium">Franchise</th>
                <th className="text-right px-4 py-3 font-medium">Cost</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {players.map((player) => (
                <tr key={player.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-900">
                    <div className="flex items-center gap-2">
                      <PlayerAvatar player={player} size={28} />
                      {player.name}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600">{player.role}</td>
                  <td className="px-4 py-3 text-gray-600">{player.franchise}</td>
                  <td className="px-4 py-3 text-right font-medium text-gray-900">{player.cost} cr</td>
                </tr>
              ))}
              {players.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                    No players in the pool for this match.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <button onClick={() => navigate("/matches")} className="mt-6 text-blue-600 hover:underline text-sm">
          ← Back to matches
        </button>
      </div>
    </div>
  );
}
