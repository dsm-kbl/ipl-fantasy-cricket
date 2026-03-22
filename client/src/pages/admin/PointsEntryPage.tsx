import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../../components/Navbar";
import apiClient from "../../api/client";
import type { MatchWithPlayers } from "../../types";

export default function PointsEntryPage() {
  const { matchId } = useParams<{ matchId: string }>();
  const [match, setMatch] = useState<MatchWithPlayers | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [pointsMap, setPointsMap] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!matchId) return;
    setLoading(true);
    apiClient
      .get<MatchWithPlayers>(`/matches/${matchId}`)
      .then((res) => {
        setMatch(res.data);
        const initial: Record<string, string> = {};
        for (const p of res.data.players) {
          initial[p.id] = "";
        }
        setPointsMap(initial);
      })
      .catch(() => setError("Failed to load match data."))
      .finally(() => setLoading(false));
  }, [matchId]);

  const updatePoints = (playerId: string, value: string) => {
    setPointsMap((prev) => ({ ...prev, [playerId]: value }));
  };

  const allFilled = match
    ? match.players.every((p) => pointsMap[p.id] !== undefined && pointsMap[p.id] !== "")
    : false;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!matchId || !allFilled) return;
    setError("");
    setSuccess("");
    setSubmitting(true);

    const points = Object.entries(pointsMap).map(([player_id, pts]) => ({
      player_id,
      points: Number.parseFloat(pts),
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
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-gray-500">Loading match data…</p>
        </div>
      </div>
    );
  }

  if (error && !match) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600">{error}</p>
          <Link to="/admin/matches" className="text-blue-600 hover:underline text-sm mt-2 inline-block">
            ← Back to matches
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Link to="/admin/matches" className="text-blue-600 hover:underline text-sm mb-4 inline-block">
          ← Back to matches
        </Link>

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

            <form onSubmit={handleSubmit}>
              <div className="bg-white rounded-lg shadow overflow-hidden mb-4">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium text-gray-700">Player</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-700">Role</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-700">Franchise</th>
                      <th className="text-left px-4 py-3 font-medium text-gray-700">Points</th>
                    </tr>
                  </thead>
                  <tbody>
                    {match.players.map((p) => (
                      <tr key={p.id} className="border-t">
                        <td className="px-4 py-3">{p.name}</td>
                        <td className="px-4 py-3">{p.role.replace("_", " ")}</td>
                        <td className="px-4 py-3">{p.franchise}</td>
                        <td className="px-4 py-3">
                          <input
                            type="number"
                            step="0.5"
                            value={pointsMap[p.id] ?? ""}
                            onChange={(e) => updatePoints(p.id, e.target.value)}
                            className="w-24 border rounded px-2 py-1 text-sm"
                            required
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {!allFilled && (
                <p className="text-amber-600 text-sm mb-3">
                  Points must be entered for all {match.players.length} players before submitting.
                </p>
              )}

              <button
                type="submit"
                disabled={!allFilled || submitting}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? "Submitting…" : "Submit Points"}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
