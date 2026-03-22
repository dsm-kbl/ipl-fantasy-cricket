import { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import apiClient from "../api/client";

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token) {
      setStatus("error");
      setMessage("No verification token provided.");
      return;
    }

    apiClient
      .get(`/auth/verify-email?token=${token}`)
      .then((res) => {
        setStatus("success");
        setMessage(res.data.message);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err.response?.data?.error?.message || "Verification failed. The link may have expired.");
      });
  }, [searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md text-center">
        <span className="text-5xl mb-4 block">
          {status === "loading" ? "⏳" : status === "success" ? "✅" : "❌"}
        </span>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {status === "loading" ? "Verifying..." : status === "success" ? "Email Verified!" : "Verification Failed"}
          </h1>
          <p className="text-sm text-gray-500 mb-6">{message || "Please wait..."}</p>

          {status === "success" && (
            <Link
              to="/dashboard"
              className="inline-block px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold text-sm hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md"
            >
              Go to Dashboard
            </Link>
          )}

          {status === "error" && (
            <Link
              to="/login"
              className="inline-block px-6 py-2.5 bg-gray-100 text-gray-700 rounded-lg font-semibold text-sm hover:bg-gray-200 transition-all"
            >
              Back to Login
            </Link>
          )}
        </div>

        <p className="text-xs text-gray-400 mt-6">
          IPL Fantasy Cricket 2026 — Build. Compete. Win.
        </p>
      </div>
    </div>
  );
}
