import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../../components/Navbar";
import apiClient from "../../api/client";
import type { MatchOut } from "../../types";

const STATUSES = ["UPCOMING", "LOCKED", "IN_PROGRESS", "COMPLETED"] as const;

const emptyForm = { team_a: "", team_b: "", venue: "", start_time: "", status: "UPCOMING" };

export default function MatchManagementPage() {
  const [matches, setMatches] = useState<MatchOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);

  const fetchMatches = () => {
    setLoading(true);
    apiClient
      .get<MatchOut[]>("/matches")
      .then((res) => setMatches(res.data))
      .catch(() => setError("Failed to load matches."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMatches();
  }, []);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setShowForm(false);
    setError("");
    setSuccess("");
  };

  const handleEdit = (match: MatchOut) => {
    setForm({
      team_a: match.team_a,
      team_b: match.team_b,
      venue: match.venue,
      start_time: match.start_time.slice(0, 16),
      status: match.status,
    });
    setEditingId(match.id);
    setShowForm(true);
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    const payload = {
      team_a: form.team_a.trim(),
      team_b: form.team_b.trim(),
      venue: form.venue.trim(),
      start_time: form.start_time,
      status: form.status,
    };

    if (!payload.team_a || !payload.team_b || !payload.venue || !payload.start_time) {
      setError("All fields are required.");
      return;
    }

    try {
      if (editingId) {
        await apiClient.put(`/admin/matches/${editingId}`, payload);
        setSuccess("Match updated.");
      } else {
        await apiClient.post("/admin/matches", payload);
        setSuccess("Match created.");
      }
      resetForm();
      fetchMatches();
    } catch {
      setError("Failed to save match.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Match Management</h1>
          <div className="flex gap-2">
            {!showForm && (
              <button
                onClick={() => { setShowForm(true); setEditingId(null); setForm(emptyForm); }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                Create Match
              </button>
            )}
          </div>
        </div>

        {error && <p className="text-red-600 mb-4">{error}</p>}
        {success && <p className="text-green-600 mb-4">{success}</p>}

        {showForm && (
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-5 mb-6 space-y-4">
            <h2 className="text-lg font-semibold">{editingId ? "Edit Match" : "Create Match"}</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="match-team-a" className="block text-sm font-medium text-gray-700 mb-1">Team A</label>
                <input
                  id="match-team-a"
                  type="text"
                  value={form.team_a}
                  onChange={(e) => setForm({ ...form, team_a: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="match-team-b" className="block text-sm font-medium text-gray-700 mb-1">Team B</label>
                <input
                  id="match-team-b"
                  type="text"
                  value={form.team_b}
                  onChange={(e) => setForm({ ...form, team_b: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="match-venue" className="block text-sm font-medium text-gray-700 mb-1">Venue</label>
                <input
                  id="match-venue"
                  type="text"
                  value={form.venue}
                  onChange={(e) => setForm({ ...form, venue: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="match-start-time" className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
                <input
                  id="match-start-time"
                  type="datetime-local"
                  value={form.start_time}
                  onChange={(e) => setForm({ ...form, start_time: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="match-status" className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                <select
                  id="match-status"
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                >
                  {STATUSES.map((s) => (
                    <option key={s} value={s}>{s.replace("_", " ")}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                {editingId ? "Update" : "Create"}
              </button>
              <button type="button" onClick={resetForm} className="px-4 py-2 border rounded text-sm hover:bg-gray-50">
                Cancel
              </button>
            </div>
          </form>
        )}

        {loading && <p className="text-gray-500">Loading matches…</p>}

        {!loading && matches.length === 0 && <p className="text-gray-500">No matches found.</p>}

        {!loading && matches.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Team A</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Team B</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Venue</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Start Time</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {matches.map((m) => {
                  const date = new Date(m.start_time);
                  return (
                    <tr key={m.id} className="border-t">
                      <td className="px-4 py-3">{m.team_a}</td>
                      <td className="px-4 py-3">{m.team_b}</td>
                      <td className="px-4 py-3">{m.venue}</td>
                      <td className="px-4 py-3">{date.toLocaleString()}</td>
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-700">{m.status}</span>
                      </td>
                      <td className="px-4 py-3 space-x-2">
                        <button onClick={() => handleEdit(m)} className="text-blue-600 hover:underline text-sm">
                          Edit
                        </button>
                        <Link to={`/admin/points/${m.id}`} className="text-green-600 hover:underline text-sm">
                          Points
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
