import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import PageBackground from "../components/PageBackground";
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
    <PageBackground>
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900">Upcoming Matches</h1>
          <p className="text-sm text-gray-500 mt-1">Pick a match and build your dream XI</p>
        </div>

        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
            <p className="text-gray-500 mt-3 text-sm">Loading matches…</p>
          </div>
        )}
        {error && <p className="text-red-600 bg-red-50 p-4 rounded-xl">{error}</p>}

        {!loading && !error && matches.length === 0 && (
          <div className="text-center py-16 bg-white rounded-2xl shadow-sm border border-gray-100">
            <span className="text-4xl">🏏</span>
            <p className="text-gray-400 mt-3">No upcoming matches found.</p>
          </div>
        )}

        <div className="grid gap-4">
          {matches.map((match) => {
            const date = new Date(match.start_time);
            return (
              <Link
                key={match.id}
                to={`/matches/${match.id}`}
                className="group block bg-white rounded-2xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition-all p-5"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🏏</span>
                    <span className="text-lg font-bold text-gray-900 group-hover:text-blue-700 transition">
                      {match.team_a} <span className="text-gray-400 font-normal">vs</span> {match.team_b}
                    </span>
                  </div>
                  <span className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 text-blue-600 border border-blue-100">
                    {match.status}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="flex items-center gap-1">
                    📅 {date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })}
                  </span>
                  <span className="flex items-center gap-1">
                    🕐 {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                  <span className="flex items-center gap-1">📍 {match.venue}</span>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </PageBackground>
  );
}
