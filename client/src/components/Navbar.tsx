import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { RulesButton } from "./RulesModal";
import FeedbackModal from "./FeedbackModal";

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path: string) => location.pathname === path;

  const linkClass = (path: string) =>
    `px-3 py-1.5 rounded-lg text-sm font-medium transition ${
      isActive(path)
        ? "bg-white/20 text-white"
        : "text-blue-100 hover:bg-white/10 hover:text-white"
    }`;

  return (
    <nav className="bg-gradient-to-r from-blue-700 via-indigo-700 to-purple-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <Link to="/dashboard" className="flex items-center gap-2">
            <span className="text-xl">🏏</span>
            <span className="text-lg font-extrabold text-white tracking-tight">IPL Fantasy</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            <Link to="/dashboard" className={linkClass("/dashboard")}>Dashboard</Link>
            <Link to="/matches" className={linkClass("/matches")}>Matches</Link>
            <Link to="/leaderboard" className={linkClass("/leaderboard")}>Leaderboard</Link>
            <RulesButton />
            <button
              onClick={() => setShowFeedback(true)}
              className="px-3 py-1.5 rounded-lg text-sm font-medium text-blue-100 hover:bg-white/10 hover:text-white transition"
            >
              Feedback
            </button>

            {isAdmin && (
              <>
                <span className="w-px h-5 bg-white/20 mx-1" />
                <Link to="/admin/players" className={linkClass("/admin/players")}>Players</Link>
                <Link to="/admin/matches" className={linkClass("/admin/matches")}>Manage</Link>
              </>
            )}

            <span className="w-px h-5 bg-white/20 mx-1" />
            <span className="text-xs text-blue-200 px-2">{user?.username}</span>
            <Link
              to="/settings"
              className="px-2 py-1.5 text-blue-200 hover:bg-white/10 hover:text-white rounded-lg transition"
              title="Settings"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </Link>
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 text-xs font-medium text-blue-200 rounded-lg hover:bg-white/10 hover:text-white transition"
            >
              Logout
            </button>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden text-white p-1"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {menuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden pb-3 space-y-1">
            <Link to="/dashboard" className="block px-3 py-2 text-sm text-blue-100 hover:bg-white/10 rounded-lg" onClick={() => setMenuOpen(false)}>Dashboard</Link>
            <Link to="/matches" className="block px-3 py-2 text-sm text-blue-100 hover:bg-white/10 rounded-lg" onClick={() => setMenuOpen(false)}>Matches</Link>
            <Link to="/leaderboard" className="block px-3 py-2 text-sm text-blue-100 hover:bg-white/10 rounded-lg" onClick={() => setMenuOpen(false)}>Leaderboard</Link>
            <button
              onClick={() => { setShowFeedback(true); setMenuOpen(false); }}
              className="block w-full text-left px-3 py-2 text-sm text-blue-100 hover:bg-white/10 rounded-lg"
            >
              Feedback
            </button>
            {isAdmin && (
              <>
                <Link to="/admin/players" className="block px-3 py-2 text-sm text-blue-100 hover:bg-white/10 rounded-lg" onClick={() => setMenuOpen(false)}>Players</Link>
                <Link to="/admin/matches" className="block px-3 py-2 text-sm text-blue-100 hover:bg-white/10 rounded-lg" onClick={() => setMenuOpen(false)}>Manage Matches</Link>
              </>
            )}
            <Link to="/settings" className="block px-3 py-2 text-sm text-blue-100 hover:bg-white/10 rounded-lg" onClick={() => setMenuOpen(false)}>Settings</Link>
            <div className="flex items-center justify-between px-3 pt-2 border-t border-white/10">
              <span className="text-xs text-blue-200">{user?.username}</span>
              <button onClick={handleLogout} className="text-xs text-blue-200 hover:text-white">Logout</button>
            </div>
          </div>
        )}
      </div>
      {showFeedback && <FeedbackModal onClose={() => setShowFeedback(false)} />}
    </nav>
  );
}
