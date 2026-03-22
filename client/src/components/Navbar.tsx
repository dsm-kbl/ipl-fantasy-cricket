import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
        <Link to="/dashboard" className="text-lg font-bold text-blue-600">
          IPL Fantasy
        </Link>

        <div className="flex items-center gap-4 text-sm">
          <Link to="/matches" className="text-gray-700 hover:text-blue-600">
            Matches
          </Link>
          <Link to="/dashboard" className="text-gray-700 hover:text-blue-600">
            Dashboard
          </Link>
          <Link to="/leaderboard" className="text-gray-700 hover:text-blue-600">
            Leaderboard
          </Link>

          {isAdmin && (
            <>
              <Link to="/admin/players" className="text-gray-700 hover:text-blue-600">
                Players
              </Link>
              <Link to="/admin/matches" className="text-gray-700 hover:text-blue-600">
                Manage Matches
              </Link>
            </>
          )}

          <span className="text-gray-500">{user?.username}</span>
          <button
            onClick={handleLogout}
            className="px-3 py-1 text-red-600 border border-red-300 rounded hover:bg-red-50"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
