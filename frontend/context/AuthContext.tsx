"use client";

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { apiPost } from "@/lib/api";

interface AuthState {
  token: string | null;
  username: string | null;
  displayName: string | null;
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    token: null,
    username: null,
    displayName: null,
  });

  useEffect(() => {
    const saved = localStorage.getItem("whist_auth");
    if (saved) {
      try {
        setState(JSON.parse(saved));
      } catch {
        localStorage.removeItem("whist_auth");
      }
    }
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const res = await apiPost<{ token: string; display_name: string }>("/api/login", {
      username,
      password,
    });
    const newState: AuthState = {
      token: res.token,
      username,
      displayName: res.display_name,
    };
    setState(newState);
    localStorage.setItem("whist_auth", JSON.stringify(newState));
  }, []);

  const logout = useCallback(() => {
    setState({ token: null, username: null, displayName: null });
    localStorage.removeItem("whist_auth");
  }, []);

  return (
    <AuthContext.Provider
      value={{ ...state, login, logout, isAuthenticated: !!state.token }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
