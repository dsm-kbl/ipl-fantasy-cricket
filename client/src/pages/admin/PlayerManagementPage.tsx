import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import apiClient from "../../api/client";
import type { PlayerOut } from "../../types";

const ROLES = ["BATSMAN", "BOWLER", "ALL_ROUNDER", "WICKET_KEEPER"] as const;

const emptyForm = { name: "", role: "BATSMAN", franchise: "", cost: "" };

export default function PlayerManagementPage() {
  const [players, setPlayers] = useState<PlayerOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);

  const fetchPlayers = () => {
    setLoading(true);
    apiClient
      .get<PlayerOut[]>("/admin/players")
      .then((res) => setPlayers(res.data))
      .catch(() => setError("Failed to load players."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPlayers();
  }, []);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setShowForm(false);
    setError("");
    setSuccess("");
  };

  const handleEdit = (player: PlayerOut) => {
    setForm({
      name: player.name,
      role: player.role,
      franchise: player.franchise,
      cost: String(player.cost),
    });
    setEditingId(player.id);
    setShowForm(true);
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    const payload = {
      name: form.name.trim(),
      role: form.role,
      franchise: form.franchise.trim(),
      cost: Number.parseFloat(form.cost),
    };

    if (!payload.name || !payload.franchise || Number.isNaN(payload.cost)) {
      setError("All fields are required and cost must be a number.");
      return;
    }

    try {
      if (editingId) {
        await apiClient.put(`/admin/players/${editingId}`, payload);
        setSuccess("Player updated.");
      } else {
        await apiClient.post("/admin/players", payload);
        setSuccess("Player added.");
      }
      resetForm();
      fetchPlayers();
    } catch {
      setError("Failed to save player.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Player Management</h1>
          <div className="flex gap-2">
            {!showForm && (
              <button
                onClick={() => { setShowForm(true); setEditingId(null); setForm(emptyForm); }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                Add Player
              </button>
            )}
          </div>
        </div>

        {error && <p className="text-red-600 mb-4">{error}</p>}
        {success && <p className="text-green-600 mb-4">{success}</p>}

        {showForm && (
          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-5 mb-6 space-y-4">
            <h2 className="text-lg font-semibold">{editingId ? "Edit Player" : "Add Player"}</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="player-name" className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  id="player-name"
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="player-role" className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  id="player-role"
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                >
                  {ROLES.map((r) => (
                    <option key={r} value={r}>{r.replace("_", " ")}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="player-franchise" className="block text-sm font-medium text-gray-700 mb-1">Franchise</label>
                <input
                  id="player-franchise"
                  type="text"
                  value={form.franchise}
                  onChange={(e) => setForm({ ...form, franchise: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
              <div>
                <label htmlFor="player-cost" className="block text-sm font-medium text-gray-700 mb-1">Cost</label>
                <input
                  id="player-cost"
                  type="number"
                  step="0.5"
                  min="0"
                  value={form.cost}
                  onChange={(e) => setForm({ ...form, cost: e.target.value })}
                  className="w-full border rounded px-3 py-2 text-sm"
                  required
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                {editingId ? "Update" : "Add"}
              </button>
              <button type="button" onClick={resetForm} className="px-4 py-2 border rounded text-sm hover:bg-gray-50">
                Cancel
              </button>
            </div>
          </form>
        )}

        {loading && <p className="text-gray-500">Loading players…</p>}

        {!loading && players.length === 0 && <p className="text-gray-500">No players found.</p>}

        {!loading && players.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Name</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Role</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Franchise</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Cost</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {players.map((p) => (
                  <tr key={p.id} className="border-t">
                    <td className="px-4 py-3">{p.name}</td>
                    <td className="px-4 py-3">{p.role.replace("_", " ")}</td>
                    <td className="px-4 py-3">{p.franchise}</td>
                    <td className="px-4 py-3">{p.cost}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleEdit(p)}
                        className="text-blue-600 hover:underline text-sm"
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
