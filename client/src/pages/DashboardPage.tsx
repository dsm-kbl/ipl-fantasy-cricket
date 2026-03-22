import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import apiClient from "../api/client";
import type { DashboardResponse } from "../types";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await apiClient.get<DashboardResponse>("/dashboard");
        setData(res.data);
      } catch {
        setError("Failed to load dashboard.");
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <p className="text-center text-gray-500 mt-12">Loading dashboard…</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <p className="text-red-600">{error || "Unable to load dashboard."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

        {/* Overall Rank */}
        <div className="bg-white rounded-lg shadow p-5 mb-6 text-center">
          <p className="text-sm text-gray-500 mb-1">Overall Rank</p>
          <p className="text-4xl font-bold text-blue-600">
            {data.overall_rank == null ? "—" : `#${data.overall_rank}`}
          </p>
          {data.overall_rank == null && (
            <p className="text-xs text-gray-400 mt-1">Participate in a match to get ranked</p>
          )}
        </div>

        {/* Participated Matches */}
        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Match History</h2>
          {data.participated_matches.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-6 text-center text-gray-400 text-sm">
              No matches played yet.
            </div>
          ) : (
            <div className="space-y-2">
              {data.participated_matches.map((pm) => {
                const date = new Date(pm.match.start_time);
                return (
                  <Link
                    key={pm.team_id}
                    to={`/dashboard/match/${pm.match.id}`}
                    className="block bg-white rounded-lg shadow p-4 hover:bg-gray-50 transition"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {pm.match.team_a} vs {pm.match.team_b}
                        </p>
                        <p className="text-xs text-gray-500">
                          {date.toLocaleDateString()} · {pm.match.venue}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-blue-600">{pm.total_score}</p>
                        <p className="text-xs text-gray-400">pts</p>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </section>

        {/* Upcoming Matches */}
        <section>
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Upcoming Matches</h2>
          {data.upcoming_matches.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-6 text-center text-gray-400 text-sm">
              No upcoming matches.
            </div>
          ) : (
            <div className="space-y-2">
              {data.upcoming_matches.map((um) => {
                const date = new Date(um.match.start_time);
                let badgeColor = "bg-gray-100 text-gray-600";
                if (um.status === "created") badgeColor = "bg-green-100 text-green-700";
                else if (um.status === "locked") badgeColor = "bg-yellow-100 text-yellow-700";
                else if (um.status === "not created") badgeColor = "bg-red-100 text-red-600";

                return (
                  <div
                    key={um.match.id}
                    className="bg-white rounded-lg shadow p-4"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {um.match.team_a} vs {um.match.team_b}
                        </p>
                        <p className="text-xs text-gray-500">
                          {date.toLocaleDateString()} · {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} · {um.match.venue}
                        </p>
                      </div>
                      <span className={`text-xs font-medium px-2 py-1 rounded ${badgeColor}`}>
                        {um.status}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
