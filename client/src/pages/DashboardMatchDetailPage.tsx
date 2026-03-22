import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
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
    const fetchDetail = async () => {
      try {
        const res = await apiClient.get<DashboardMatchDetail>(`/dashboard/match/${id}`);
        setDetail(res.data);
      } catch {
        setError("Failed to load match details.");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <p className="text-center text-gray-500 mt-12">Loading match details…</p>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600">{error || "Match detail not found."}</p>
          <button
            onClick={() => navigate("/dashboard")}
            className="mt-4 text-blue-600 hover:underline text-sm"
          >
            ← Back to dashboard
          </button>
        </div>
      </div>
    );
  }

  const { match, players, total_score } = detail;
  const date = new Date(match.start_time);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Match header */}
        <div className="bg-white rounded-lg shadow p-5 mb-6">
          <h1 className="text-xl font-bold text-gray-900 mb-1">
            {match.team_a} vs {match.team_b}
          </h1>
          <p className="text-sm text-gray-600">
            📅 {date.toLocaleDateString()} · 🕐{" "}
            {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} · 📍 {match.venue}
          </p>
          <div className="mt-3 flex items-center gap-3">
            <span className="text-xs font-medium px-2 py-1 rounded bg-blue-100 text-blue-700">
              {match.status}
            </span>
            <span className="text-sm font-semibold text-gray-700">
              Total Score: <span className="text-blue-600">{total_score}</span>
            </span>
          </div>
        </div>

        {/* Team composition table */}
        <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
          <div className="p-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-800">Team Composition</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600 text-left">
                <tr>
                  <th className="px-4 py-3 font-medium">#</th>
                  <th className="px-4 py-3 font-medium">Player</th>
                  <th className="px-4 py-3 font-medium">Role</th>
                  <th className="px-4 py-3 font-medium">Franchise</th>
                  <th className="px-4 py-3 font-medium text-right">Cost</th>
                  <th className="px-4 py-3 font-medium text-right">Points</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {players.map((player, idx) => (
                  <tr key={player.player_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-500">{idx + 1}</td>
                    <td className="px-4 py-3 font-medium text-gray-900">{player.player_name}</td>
                    <td className="px-4 py-3 text-gray-600">{ROLE_LABELS[player.role] || player.role}</td>
                    <td className="px-4 py-3 text-gray-600">{player.franchise}</td>
                    <td className="px-4 py-3 text-right text-gray-600">{player.cost}</td>
                    <td className="px-4 py-3 text-right font-semibold text-blue-600">
                      {player.points ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50">
                <tr>
                  <td colSpan={5} className="px-4 py-3 font-semibold text-gray-800 text-right">
                    Total
                  </td>
                  <td className="px-4 py-3 text-right font-bold text-blue-600">
                    {total_score}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <button
          onClick={() => navigate("/dashboard")}
          className="text-blue-600 hover:underline text-sm"
        >
          ← Back to dashboard
        </button>
      </div>
    </div>
  );
}
