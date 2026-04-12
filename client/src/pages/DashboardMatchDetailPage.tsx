import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import PageBackground from "../components/PageBackground";
import apiClient from "../api/client";
import type { DashboardMatchDetail } from "../types";

const ROLE_LABELS: Record<string, string> = {
  WICKET_KEEPER: "WK",
  BATSMAN: "BAT",
  BOWLER: "BOWL",
  ALL_ROUNDER: "AR",
};

export default function DashboardMatchDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<DashboardMatchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    apiClient
      .get<DashboardMatchDetail>(`/dashboard/match/${id}`)
      .then((res) => setDetail(res.data))
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

  if (error || !detail) {
    return (
      <PageBackground>
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600 bg-red-50 p-4 rounded-xl">{error}</p>
          <button onClick={() => navigate("/dashboard")} className="mt-4 text-blue-600 hover:underline text-sm">← Back</button>
        </div>
      </PageBackground>
    );
  }

  const { match, players, total_score, toss_prediction, motm_prediction, motm_player_name } = detail;
  const date = new Date(match.start_time);

  const isCompleted = match.status === "COMPLETED";
  const tossCorrect = isCompleted && match.toss_winner && toss_prediction
    ? toss_prediction.trim().toLowerCase() === match.toss_winner.trim().toLowerCase()
    : null;
  const motmCorrect = isCompleted && match.motm_player_id && motm_prediction
    ? motm_prediction === match.motm_player_id
    : null;

  return (
    <PageBackground>
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Match header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-lg p-6 mb-6 text-white">
          <h1 className="text-2xl font-extrabold mb-1">{match.team_a} vs {match.team_b}</h1>
          <div className="flex items-center gap-4 text-sm text-blue-200">
            <span>📅 {date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}</span>
            <span>🕐 {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
            <span>📍 {match.venue}</span>
          </div>
          <div className="mt-4 flex items-center gap-4">
            <span className="text-xs font-semibold px-3 py-1 rounded-full bg-white/20">{match.status}</span>
            <span className="text-lg font-extrabold">Score: {total_score} pts</span>
          </div>
        </div>

        {/* Bonus Predictions */}
        {(toss_prediction || motm_prediction) && (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
            <div className="px-5 py-4 border-b border-gray-100">
              <h2 className="text-lg font-bold text-gray-900">🎯 Bonus Predictions</h2>
            </div>
            <div className="px-5 py-4 space-y-3">
              {toss_prediction && (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-500">🪙 Toss Winner</p>
                    <p className="text-sm font-medium text-gray-900">{toss_prediction}</p>
                  </div>
                  {tossCorrect !== null && (
                    <span className={`text-sm font-semibold px-3 py-1 rounded-full ${tossCorrect ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                      {tossCorrect ? "✅ +10 pts" : "❌ 0 pts"}
                    </span>
                  )}
                </div>
              )}
              {motm_prediction && (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-gray-500">⭐ Man of the Match</p>
                    <p className="text-sm font-medium text-gray-900">{motm_player_name || "Unknown player"}</p>
                  </div>
                  {motmCorrect !== null && (
                    <span className={`text-sm font-semibold px-3 py-1 rounded-full ${motmCorrect ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                      {motmCorrect ? "✅ +25 pts" : "❌ 0 pts"}
                    </span>
                  )}
                </div>
              )}
              {!isCompleted && (
                <p className="text-xs text-gray-400">Results will be shown after the match is completed.</p>
              )}
            </div>
          </div>
        )}

        {/* Team composition */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
          <div className="px-5 py-4 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900">Your Team</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  <th className="text-left px-5 py-3 font-medium">#</th>
                  <th className="text-left px-5 py-3 font-medium">Player</th>
                  <th className="text-left px-5 py-3 font-medium">Role</th>
                  <th className="text-left px-5 py-3 font-medium">Franchise</th>
                  <th className="text-right px-5 py-3 font-medium">Cost</th>
                  <th className="text-right px-5 py-3 font-medium">Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {players.map((player, idx) => (
                  <tr key={player.player_id} className="hover:bg-blue-50/30 transition">
                    <td className="px-5 py-3 text-gray-400">{idx + 1}</td>
                    <td className="px-5 py-3 font-medium text-gray-900">{player.player_name}</td>
                    <td className="px-5 py-3 text-gray-500">{ROLE_LABELS[player.role] || player.role}</td>
                    <td className="px-5 py-3 text-gray-500">{player.franchise}</td>
                    <td className="px-5 py-3 text-right text-gray-500">{player.cost}</td>
                    <td className="px-5 py-3 text-right font-bold text-blue-600">{player.points ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50">
                <tr>
                  <td colSpan={5} className="px-5 py-3 font-bold text-gray-800 text-right">Total</td>
                  <td className="px-5 py-3 text-right font-extrabold text-blue-600">{total_score}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <button onClick={() => navigate("/dashboard")} className="text-blue-600 hover:underline text-sm">← Back to dashboard</button>
      </div>
    </PageBackground>
  );
}
