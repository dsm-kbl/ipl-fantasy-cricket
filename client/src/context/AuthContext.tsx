import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  type ReactNode,
} from "react";
import apiClient from "../api/client";
import type { UserOut, AuthTokenResponse } from "../types";

interface AuthContextType {
  user: UserOut | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (
    username: string,
    email: string,
    password: string
  ) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await apiClient.post<AuthTokenResponse>("/auth/login", {
      email,
      password,
    });
    const { user: loggedInUser, token: authToken } = response.data;
    localStorage.setItem("token", authToken);
    localStorage.setItem("user", JSON.stringify(loggedInUser));
    setToken(authToken);
    setUser(loggedInUser);
  }, []);

  const register = useCallback(
    async (username: string, email: string, password: string) => {
      const response = await apiClient.post<AuthTokenResponse>(
        "/auth/register",
        { username, email, password }
      );
      const { user: newUser, token: authToken } = response.data;
      localStorage.setItem("token", authToken);
      localStorage.setItem("user", JSON.stringify(newUser));
      setToken(authToken);
      setUser(newUser);
    },
    []
  );

  const logout = useCallback(() => {
    apiClient.post("/auth/logout").catch(() => {
      /* ignore errors on logout */
    });
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }, []);

  const value: AuthContextType = useMemo(
    () => ({
      user,
      token,
      isLoading,
      login,
      register,
      logout,
      isAuthenticated: !!token && !!user,
      isAdmin: user?.role === "ADMIN",
    }),
    [user, token, isLoading, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
