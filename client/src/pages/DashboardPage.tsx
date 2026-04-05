import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import PageBackground from "../components/PageBackground";
import RulesModal from "../components/RulesModal";
import { useAuth } from "../context/AuthContext";
import apiClient from "../api/client";
import type { DashboardResponse } from "../types";

export default function DashboardPage() {
  const { isAdmin } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiClient
      .get<DashboardResponse>("/dashboard")
      .then((res) => setData(res.data))
      .catch(() => setError("Failed to load dashboard."))
      .finally(() => setLoading(false));
  }, []);

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
          <p className="text-red-600 bg-red-50 p-4 rounded-xl">{error}</p>
        </div>
      </PageBackground>
    );
  }

  return (
    <PageBackground>
      <Navbar />
      <RulesModal />
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-6">Dashboard</h1>

        {/* Next match day CTA(s) */}
        {data.upcoming_matches.length > 0 && (() => {
          // Group CTA cards for all matches on the nearest match day
          const firstDate = new Date(data.upcoming_matches[0].match.start_time);
          const firstDay = firstDate.toDateString();
          const todayMatches = data.upcoming_matches.filter(
            (um) => new Date(um.match.start_time).toDateString() === firstDay
          );
          return todayMatches.map((um) => {
            const date = new Date(um.match.start_time);
            const msUntil = date.getTime() - Date.now();
            const hoursUntil = Math.max(0, msUntil / (1000 * 60 * 60));
            const hoursSinceStart = Math.max(0, -msUntil / (1000 * 60 * 60));
            const hasCompleted = hoursSinceStart >= 4;
            const hasStarted = msUntil <= 0 && !hasCompleted;
            const isUrgent = !hasStarted && !hasCompleted && hoursUntil < 3;
            return (
              <Link
                key={um.match.id}
                to={um.status === "created" || isAdmin ? `/dashboard` : `/team-builder/${um.match.id}`}
                className={`block rounded-2xl shadow-lg p-5 mb-4 transition-all hover:shadow-xl ${
                  hasCompleted
                    ? "bg-gradient-to-r from-gray-500 to-gray-600 text-white"
                    : hasStarted
                      ? "bg-gradient-to-r from-purple-600 to-indigo-600 text-white"
                      : isUrgent
                        ? "bg-gradient-to-r from-orange-500 to-red-500 text-white"
                        : "bg-gradient-to-r from-emerald-500 to-teal-500 text-white"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium opacity-80 mb-1">
                      {hasCompleted ? "✅ Match Completed" : hasStarted ? "🏏 Match In Progress" : isUrgent ? "⏰ Match starting soon!" : "🏏 Next Match"}
                    </p>
                    <p className="text-lg font-extrabold">
                      {um.match.team_a} vs {um.match.team_b}
                    </p>
                    <p className="text-sm opacity-80 mt-1">
                      {date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })} · {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </p>
                  </div>
                  <div className="text-right">
                    {um.status === "not created" ? (
                      <span className="inline-block px-4 py-2 bg-white/20 rounded-xl text-sm font-bold hover:bg-white/30 transition">
                        Build Team →
                      </span>
                    ) : um.status === "created" ? (
                      <span className="inline-block px-4 py-2 bg-white/20 rounded-xl text-sm font-bold">
                        ✓ Team Ready
                      </span>
                    ) : (
                      <span className="inline-block px-4 py-2 bg-white/20 rounded-xl text-sm font-bold">
                        🔒 Locked
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            );
          });
        })()}

        {/* Overall Rank */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-lg p-6 mb-8 text-center text-white">
          <p className="text-sm text-blue-200 mb-1">Your Overall Rank</p>
          <p className="text-5xl font-extrabold">
            {data.overall_rank == null ? "—" : `#${data.overall_rank}`}
          </p>
          {data.overall_rank == null && (
            <p className="text-xs text-blue-200 mt-2">Participate in a match to get ranked</p>
          )}
        </div>

        {/* Match History */}
        <section className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Match History</h2>
          {data.participated_matches.length === 0 ? (
            <div className="bg-white/80 backdrop-blur rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
              <span className="text-3xl">📊</span>
              <p className="text-gray-400 mt-2 text-sm">No matches played yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data.participated_matches.map((pm) => {
                const date = new Date(pm.match.start_time);
                return (
                  <Link
                    key={pm.team_id}
                    to={`/dashboard/match/${pm.match.id}`}
                    className="group flex items-center justify-between bg-white/80 backdrop-blur rounded-2xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition-all p-4"
                  >
                    <div>
                      <p className="text-sm font-bold text-gray-900 group-hover:text-blue-700 transition">
                        {pm.match.team_a} vs {pm.match.team_b}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {date.toLocaleDateString(undefined, { month: "short", day: "numeric" })} · {pm.match.venue}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-extrabold text-blue-600">{pm.total_score}</p>
                      <p className="text-[10px] text-gray-400 uppercase tracking-wide">pts</p>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </section>

        {/* Upcoming Matches */}
        <section>
          <h2 className="text-xl font-bold text-gray-900 mb-4">Upcoming Matches</h2>
          {data.upcoming_matches.length === 0 ? (
            <div className="bg-white/80 backdrop-blur rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
              <span className="text-3xl">📅</span>
              <p className="text-gray-400 mt-2 text-sm">No upcoming matches.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data.upcoming_matches.map((um) => {
                const date = new Date(um.match.start_time);
                let badgeClass = "bg-gray-100 text-gray-500 border-gray-200";
                if (um.status === "created") badgeClass = "bg-green-50 text-green-600 border-green-200";
                else if (um.status === "locked") badgeClass = "bg-yellow-50 text-yellow-600 border-yellow-200";
                else if (um.status === "not created") badgeClass = "bg-red-50 text-red-500 border-red-200";
                return (
                  <div key={um.match.id} className="flex items-center justify-between bg-white/80 backdrop-blur rounded-2xl shadow-sm border border-gray-100 p-4">
                    <div>
                      <p className="text-sm font-bold text-gray-900">{um.match.team_a} vs {um.match.team_b}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {date.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" })} · {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} · {um.match.venue}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {um.status === "not created" && !isAdmin && (
                        <Link
                          to={`/team-builder/${um.match.id}`}
                          className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition"
                        >
                          Build Team
                        </Link>
                      )}
                      <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${badgeClass}`}>{um.status}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </PageBackground>
  );
}
