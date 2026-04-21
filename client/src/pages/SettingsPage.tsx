import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import PageBackground from "../components/PageBackground";
import apiClient from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { UserOut } from "../types";

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [notificationsEnabled, setNotificationsEnabled] = useState(user?.notifications_enabled ?? true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleToggle = async () => {
    const newValue = !notificationsEnabled;
    setNotificationsEnabled(newValue);
    setSaving(true);
    setMessage("");
    setError("");

    try {
      const res = await apiClient.patch<UserOut>("/auth/settings", {
        notifications_enabled: newValue,
      });
      await refreshUser(res.data);
      setMessage(newValue ? "Match reminders enabled" : "Match reminders disabled");
    } catch {
      setNotificationsEnabled(!newValue);
      setError("Failed to update settings. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <PageBackground>
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-extrabold text-gray-900 mb-6">Settings</h1>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="px-6 py-5 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900">Account</h2>
            <p className="text-sm text-gray-500 mt-1">Signed in as <span className="font-medium text-gray-700">{user?.username}</span> ({user?.email})</p>
          </div>

          <div className="px-6 py-5 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-900 mb-1">🔔 Notifications</h2>
            <p className="text-sm text-gray-500 mb-4">Get an email reminder 1 hour and 30 minutes before a match when you haven't built your team yet.</p>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
              <div>
                <p className="text-sm font-semibold text-gray-900">Match reminders</p>
                <p className="text-xs text-gray-500 mt-0.5">Email notifications before matches</p>
              </div>
              <button
                type="button"
                onClick={handleToggle}
                disabled={saving}
                aria-label="Toggle match reminders"
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 ${
                  notificationsEnabled ? "bg-blue-600" : "bg-gray-300"
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition duration-200 ease-in-out ${
                    notificationsEnabled ? "translate-x-5" : "translate-x-0"
                  }`}
                />
              </button>
            </div>

            {message && <p className="mt-3 text-sm text-green-600">✓ {message}</p>}
            {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
          </div>
        </div>

        <button
          onClick={() => navigate(-1)}
          className="mt-6 text-blue-600 hover:underline text-sm"
        >
          ← Back
        </button>
      </div>
    </PageBackground>
  );
}
