import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { AxiosError } from "axios";
import type { ErrorResponse } from "../types";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [registered, setRegistered] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFieldErrors({});
    setGeneralError("");
    setIsSubmitting(true);

    try {
      // Call API directly instead of auth context (no auto-login)
      const { default: apiClient } = await import("../api/client");
      await apiClient.post("/auth/register", { username, email, password });
      setRegistered(true);
    } catch (err) {
      const axiosError = err as AxiosError<ErrorResponse>;
      const respData = axiosError.response?.data as Record<string, unknown> | undefined;
      const errorData = (respData?.error ?? (respData?.detail as Record<string, unknown>)?.error) as { message?: string; details?: Array<{ field?: string; message: string }> } | undefined;
      const details = errorData?.details ?? [];

      const errors: Record<string, string> = {};
      const generalMessages: string[] = [];

      for (const detail of details) {
        if (detail.field) {
          errors[detail.field] = detail.message;
        } else {
          generalMessages.push(detail.message);
        }
      }

      setFieldErrors(errors);
      setGeneralError(
        generalMessages[0] ?? (details.length === 0 ? (errorData?.message ?? "Registration failed.") : "")
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputClass = (field: string) =>
    `w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm ${
      fieldErrors[field] ? "border-red-400 bg-red-50" : "border-gray-300"
    }`;

  return (
    <div className="min-h-screen flex">
      {/* Left panel - branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-purple-700 to-pink-700 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 right-10 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-10 left-10 w-96 h-96 bg-yellow-300 rounded-full blur-3xl" />
          <div className="absolute top-1/3 left-1/4 w-64 h-64 bg-blue-300 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10 flex flex-col justify-center px-16 text-white">
          <div className="mb-8">
            <span className="text-5xl">🏏</span>
          </div>
          <h1 className="text-4xl font-extrabold mb-4 leading-tight">
            Join the<br />Fantasy League
          </h1>
          <p className="text-lg text-purple-100 mb-8 max-w-md">
            Create your account, pick your dream XI from real IPL squads, and compete for the top spot on the leaderboard.
          </p>
          <div className="space-y-3 text-sm text-purple-200">
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-xs font-bold">✓</span>
              All 10 IPL 2026 teams with real squads
            </div>
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-xs font-bold">✓</span>
              100 credit budget — pick wisely
            </div>
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-xs font-bold">✓</span>
              Points based on real match performance
            </div>
          </div>
        </div>
      </div>

      {/* Right panel - register form */}
      <div className="flex-1 flex items-center justify-center bg-gray-50 px-6">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <span className="text-4xl">🏏</span>
            <h1 className="text-2xl font-extrabold text-gray-900 mt-2">IPL Fantasy Cricket</h1>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
            {registered ? (
              <>
                <div className="text-center">
                  <span className="text-5xl block mb-4">📧</span>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Check your email</h2>
                  <p className="text-sm text-gray-500 mb-6">
                    We've sent a verification link to <span className="font-semibold text-gray-700">{email}</span>. Click the link to activate your account.
                  </p>
                  <Link
                    to="/login"
                    className="inline-block px-6 py-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold text-sm hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md"
                  >
                    Go to Login
                  </Link>
                  <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-700">
                    💡 Didn't receive it? Check your spam/junk folder and mark it as "not spam".
                  </div>
                </div>
              </>
            ) : (
            <>
            <h2 className="text-2xl font-bold text-gray-900 mb-1">Create your account</h2>
            <p className="text-sm text-gray-500 mb-6">Start building your dream team today</p>

            {generalError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-center gap-2">
                <svg className="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {generalError}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="cricketfan123"
                  className={inputClass("username")}
                  required
                />
                {fieldErrors.username && (
                  <p className="mt-1 text-xs text-red-600">{fieldErrors.username}</p>
                )}
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Email address
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className={inputClass("email")}
                  required
                />
                {fieldErrors.email && (
                  <p className="mt-1 text-xs text-red-600">{fieldErrors.email}</p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className={inputClass("password")}
                  required
                />
                {fieldErrors.password && (
                  <p className="mt-1 text-xs text-red-600">{fieldErrors.password}</p>
                )}
                <p className="mt-1 text-xs text-gray-400">Minimum 8 characters</p>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 font-semibold text-sm transition-all shadow-md hover:shadow-lg"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Creating account...
                  </span>
                ) : (
                  "Create account"
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-500">
                Already have an account?{" "}
                <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-semibold">
                  Sign in
                </Link>
              </p>
            </div>
            </>
            )}
          </div>

          <p className="text-center text-xs text-gray-400 mt-6">
            IPL Fantasy Cricket 2026 — Build. Compete. Win.
          </p>
        </div>
      </div>
    </div>
  );
}
