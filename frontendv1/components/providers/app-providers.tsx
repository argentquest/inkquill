"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { fetchBalance, fetchMaintenanceStatus, fetchSession } from "@/lib/api";
import type { BalanceState, MaintenanceState, SessionState, SessionUser, ToastMessage } from "@/lib/types";
import { RouteHelpButton } from "@/components/ui/route-help-button";

const THEME_STORAGE_KEY = "frontendv1-theme";
const COOKIE_STORAGE_KEY = "frontendv1-cookie-consent";

type ThemeMode = "light" | "dark";

interface ThemeContextValue {
  theme: ThemeMode;
  setTheme: (_theme: ThemeMode) => void;
  toggleTheme: () => void;
}

interface SessionContextValue extends SessionState {
  refreshSession: () => Promise<void>;
  setAuthenticated: (_user: SessionUser) => void;
  setAnonymous: () => void;
}

interface BalanceContextValue extends BalanceState {
  loading: boolean;
  refreshBalance: () => Promise<void>;
}

interface MaintenanceContextValue extends MaintenanceState {
  loading: boolean;
  refreshMaintenance: () => Promise<void>;
}

interface CookieConsentContextValue {
  accepted: boolean;
  accept: () => void;
}

interface ToastContextValue {
  toasts: ToastMessage[];
  pushToast: (_toast: Omit<ToastMessage, "id">) => void;
  dismissToast: (_id: string) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);
const SessionContext = createContext<SessionContextValue | undefined>(undefined);
const BalanceContext = createContext<BalanceContextValue | undefined>(undefined);
const MaintenanceContext = createContext<MaintenanceContextValue | undefined>(undefined);
const CookieConsentContext = createContext<CookieConsentContextValue | undefined>(undefined);
const ToastContext = createContext<ToastContextValue | undefined>(undefined);

const fallbackThemeContext: ThemeContextValue = {
  theme: "light",
  setTheme: () => undefined,
  toggleTheme: () => undefined
};

const fallbackSessionContext: SessionContextValue = {
  status: "anonymous",
  user: null,
  error: null,
  refreshSession: async () => undefined,
  setAuthenticated: () => undefined,
  setAnonymous: () => undefined
};

const fallbackBalanceContext: BalanceContextValue = {
  balance: 0,
  currency: "Coins",
  error: "Balance unavailable",
  loading: false,
  refreshBalance: async () => undefined
};

const fallbackMaintenanceContext: MaintenanceContextValue = {
  enabled: false,
  message: null,
  updated_at: null,
  end_time: null,
  loading: false,
  refreshMaintenance: async () => undefined
};

const fallbackCookieConsentContext: CookieConsentContextValue = {
  accepted: false,
  accept: () => undefined
};

const fallbackToastContext: ToastContextValue = {
  toasts: [],
  pushToast: () => undefined,
  dismissToast: () => undefined
};

function useCreateQueryClient() {
  return useMemo(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            staleTime: 30000
          }
        }
      }),
    []
  );
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  const queryClient = useCreateQueryClient();
  const [theme, setThemeState] = useState<ThemeMode>("light");
  const [accepted, setAccepted] = useState(false);
  const [session, setSession] = useState<SessionState>({
    status: "loading",
    user: null,
    error: null
  });
  const [balance, setBalance] = useState<BalanceState>({
    balance: 0,
    currency: "Coins",
    error: undefined
  });
  const [balanceLoading, setBalanceLoading] = useState(true);
  const [maintenance, setMaintenance] = useState<MaintenanceState>({
    enabled: false,
    message: null,
    updated_at: null,
    end_time: null
  });
  const [maintenanceLoading, setMaintenanceLoading] = useState(true);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    const initialTheme = storedTheme === "dark" ? "dark" : "light";
    setThemeState(initialTheme);
    document.documentElement.dataset.theme = initialTheme;

    const storedConsent = window.localStorage.getItem(COOKIE_STORAGE_KEY);
    setAccepted(storedConsent === "accepted");
  }, []);

  const setTheme = useCallback((nextTheme: ThemeMode) => {
    setThemeState(nextTheme);
    document.documentElement.dataset.theme = nextTheme;
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((currentTheme) => {
      const nextTheme = currentTheme === "light" ? "dark" : "light";
      document.documentElement.dataset.theme = nextTheme;
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
      return nextTheme;
    });
  }, []);

  const pushToast = useCallback((toast: Omit<ToastMessage, "id">) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    setToasts((current) => [...current, { id, ...toast }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((item) => item.id !== id));
    }, 4500);
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts((current) => current.filter((item) => item.id !== id));
  }, []);

  const setAuthenticated = useCallback((user: SessionUser) => {
    setSession({
      status: "authenticated",
      user,
      error: null
    });
  }, []);

  const setAnonymous = useCallback(() => {
    setSession({
      status: "anonymous",
      user: null,
      error: null
    });
  }, []);

  const refreshSession = useCallback(async () => {
    try {
      const user = await fetchSession();
      if (user) {
        setAuthenticated(user);
      } else {
        setAnonymous();
      }
    } catch (error) {
      setSession({
        status: "error",
        user: null,
        error: error instanceof Error ? error.message : "Failed to load session"
      });
      pushToast({
        title: "Session bootstrap failed",
        tone: "warning",
        detail: "The app could not confirm your session. Retry once the service responds again."
      });
    }
  }, [pushToast, setAnonymous, setAuthenticated]);

  const refreshBalance = useCallback(async () => {
    setBalanceLoading(true);
    try {
      const data = await fetchBalance();
      setBalance(data);
    } catch (error) {
      setBalance({
        balance: 0,
        currency: "Coins",
        error: error instanceof Error ? error.message : "Failed to load balance"
      });
      pushToast({
        title: "Balance unavailable",
        tone: "warning",
        detail: "The shell will continue without live balance data."
      });
    } finally {
      setBalanceLoading(false);
    }
  }, [pushToast]);

  const refreshMaintenance = useCallback(async () => {
    setMaintenanceLoading(true);
    try {
      const data = await fetchMaintenanceStatus();
      setMaintenance(data);
    } catch (error) {
      setMaintenance({
        enabled: false,
        message: error instanceof Error ? error.message : "Failed to load maintenance status"
      });
    } finally {
      setMaintenanceLoading(false);
    }
  }, []);

  useEffect(() => {
    void refreshSession();
    void refreshBalance();
    void refreshMaintenance();
  }, [refreshBalance, refreshMaintenance, refreshSession]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      void refreshMaintenance();
    }, 60000);

    return () => window.clearInterval(interval);
  }, [refreshMaintenance]);

  const accept = useCallback(() => {
    setAccepted(true);
    window.localStorage.setItem(COOKIE_STORAGE_KEY, "accepted");
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
        <ToastContext.Provider value={{ toasts, pushToast, dismissToast }}>
          <CookieConsentContext.Provider value={{ accepted, accept }}>
            <SessionContext.Provider value={{ ...session, refreshSession, setAuthenticated, setAnonymous }}>
              <BalanceContext.Provider value={{ ...balance, loading: balanceLoading, refreshBalance }}>
                <MaintenanceContext.Provider value={{ ...maintenance, loading: maintenanceLoading, refreshMaintenance }}>
                  {children}
                  <RouteHelpButton />
                </MaintenanceContext.Provider>
              </BalanceContext.Provider>
            </SessionContext.Provider>
          </CookieConsentContext.Provider>
        </ToastContext.Provider>
      </ThemeContext.Provider>
    </QueryClientProvider>
  );
}

export function useTheme() {
  return useContext(ThemeContext) ?? fallbackThemeContext;
}

export function useSession() {
  return useContext(SessionContext) ?? fallbackSessionContext;
}

export function useBalance() {
  return useContext(BalanceContext) ?? fallbackBalanceContext;
}

export function useMaintenance() {
  return useContext(MaintenanceContext) ?? fallbackMaintenanceContext;
}

export function useCookieConsent() {
  return useContext(CookieConsentContext) ?? fallbackCookieConsentContext;
}

export function useToasts() {
  return useContext(ToastContext) ?? fallbackToastContext;
}
