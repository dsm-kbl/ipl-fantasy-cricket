import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import apiClient from "../api/client";
import type { MatchOut } from "../types";

export default function MatchesPage() {
  const [matches, setMatches] = useState<MatchOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient
      .get<MatchOut[]>("/matches")
      .then((res) => setMatches(res.data))
      .catch(() => setError("Failed to load matches."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Upcoming Matches</h1>

        {loading && <p className="text-gray-500">Loading matches…</p>}
        {error && <p className="text-red-600">{error}</p>}

        {!loading && !error && matches.length === 0 && (
          <p className="text-gray-500">No upcoming matches found.</p>
        )}

        <div className="grid gap-4">
          {matches.map((match) => {
            const date = new Date(match.start_time);
            return (
              <Link
                key={match.id}
                to={`/matches/${match.id}`}
                className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow p-5"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-lg font-semibold text-gray-900">
                    {match.team_a} vs {match.team_b}
                  </span>
                  <span className="text-xs font-medium px-2 py-1 rounded bg-blue-100 text-blue-700">
                    {match.status}
                  </span>
                </div>
                <div className="text-sm text-gray-600 space-y-1">
                  <p>📅 {date.toLocaleDateString()} · 🕐 {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</p>
                  <p>📍 {match.venue}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
