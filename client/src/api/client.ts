import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Extract a user-friendly error message from the standard API error envelope:
 *   { "error": { "code": "...", "message": "...", "details": [...] } }
 *
 * Falls back to generic messages when the response doesn't match the format.
 */
function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data;
    if (data?.error?.message) {
      return data.error.message;
    }
    if (error.response?.statusText) {
      return error.response.statusText;
    }
  }
  return "An unexpected error occurred";
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const isAuthRoute = globalThis.location.pathname === "/login" || globalThis.location.pathname === "/register";
      if (!isAuthRoute) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        globalThis.location.href = "/login";
      }
    }

    // Attach a parsed message so consuming code can use `error.userMessage`
    if (axios.isAxiosError(error)) {
      Object.assign(error, { userMessage: extractErrorMessage(error) });
    }

    return Promise.reject(error);
  }
);

export { extractErrorMessage };
export default apiClient;
