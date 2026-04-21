import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";

import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";
import MatchesPage from "./pages/MatchesPage";
import MatchDetailPage from "./pages/MatchDetailPage";
import TeamBuilderPage from "./pages/TeamBuilderPage";
import DashboardPage from "./pages/DashboardPage";
import DashboardMatchDetailPage from "./pages/DashboardMatchDetailPage";
import LeaderboardPage from "./pages/LeaderboardPage";
import PlayerManagementPage from "./pages/admin/PlayerManagementPage";
import MatchManagementPage from "./pages/admin/MatchManagementPage";
import PointsEntryPage from "./pages/admin/PointsEntryPage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public auth routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />

          {/* Protected routes */}
          <Route
            path="/matches"
            element={
              <ProtectedRoute>
                <MatchesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/matches/:id"
            element={
              <ProtectedRoute>
                <MatchDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/team-builder/:matchId"
            element={
              <ProtectedRoute>
                <TeamBuilderPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/match/:id"
            element={
              <ProtectedRoute>
                <DashboardMatchDetailPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/leaderboard"
            element={
              <ProtectedRoute>
                <LeaderboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <SettingsPage />
              </ProtectedRoute>
            }
          />

          {/* Admin routes */}
          <Route
            path="/admin/players"
            element={
              <AdminRoute>
                <PlayerManagementPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/matches"
            element={
              <AdminRoute>
                <MatchManagementPage />
              </AdminRoute>
            }
          />
          <Route
            path="/admin/points/:matchId"
            element={
              <AdminRoute>
                <PointsEntryPage />
              </AdminRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
