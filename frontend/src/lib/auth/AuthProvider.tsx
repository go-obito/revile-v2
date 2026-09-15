"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type Role, type UserRead } from "@/lib/api";

interface AuthContextValue {
  accessToken: string | null;
  user: UserRead | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: Role[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserRead | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.refresh()
      .then((session) => {
        setAccessToken(session.access_token);
        setUser(session.user);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const session = await api.login(email, password);
    setAccessToken(session.access_token);
    setUser(session.user);
  }

  async function logout() {
    await api.logout().catch(() => undefined);
    setAccessToken(null);
    setUser(null);
  }

  function hasRole(...roles: Role[]) {
    return user !== null && roles.includes(user.role);
  }

  return <AuthContext.Provider value={{ accessToken, user, loading, login, logout, hasRole }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
