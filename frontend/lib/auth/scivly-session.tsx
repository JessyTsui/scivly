"use client";

import {
  createContext,
  startTransition,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { useAuth, useUser } from "@clerk/nextjs";

import { ApiError, apiRequest } from "@/lib/api/client";
import type { AuthUserOut, BackendWorkspaceOut, PaginatedResponse } from "@/lib/api/types";

interface SessionUser {
  id: string;
  email: string | null;
  name: string;
  imageUrl: string | null;
}

interface ScivlySessionContextValue {
  backendUser: AuthUserOut | null;
  error: string | null;
  isLoaded: boolean;
  isSignedIn: boolean;
  isSyncing: boolean;
  refresh: () => Promise<void>;
  user: SessionUser | null;
  workspace: BackendWorkspaceOut | null;
}

const ScivlySessionContext = createContext<ScivlySessionContextValue | undefined>(undefined);

function buildUserSnapshot(
  clerkUser: ReturnType<typeof useUser>["user"],
  backendUser: AuthUserOut | null
): SessionUser | null {
  if (!clerkUser && !backendUser) {
    return null;
  }

  return {
    id: clerkUser?.id ?? backendUser?.id ?? "anonymous",
    email: clerkUser?.primaryEmailAddress?.emailAddress ?? backendUser?.email ?? null,
    name:
      clerkUser?.fullName ??
      clerkUser?.firstName ??
      backendUser?.name ??
      "Scivly User",
    imageUrl: clerkUser?.imageUrl ?? backendUser?.avatar_url ?? null,
  };
}

export function ScivlySessionProvider({ children }: { children: React.ReactNode }) {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const { user: clerkUser } = useUser();
  const [backendUser, setBackendUser] = useState<AuthUserOut | null>(null);
  const [workspace, setWorkspace] = useState<BackendWorkspaceOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const syncSession = useCallback(async () => {
    if (!isLoaded) {
      return;
    }

    if (!isSignedIn) {
      startTransition(() => {
        setBackendUser(null);
        setWorkspace(null);
        setError(null);
        setIsSyncing(false);
      });
      return;
    }

    setIsSyncing(true);

    try {
      const token = await getToken();

      if (!token) {
        throw new Error("Clerk did not return a session token.");
      }

      const [userResponse, workspaceResponse] = await Promise.all([
        apiRequest<AuthUserOut>("/auth/me", { authToken: token }),
        apiRequest<PaginatedResponse<BackendWorkspaceOut>>("/workspaces", { authToken: token }),
      ]);

      startTransition(() => {
        setBackendUser(userResponse);
        setWorkspace(workspaceResponse.items[0] ?? null);
        setError(null);
      });
    } catch (sessionError) {
      const message =
        sessionError instanceof ApiError || sessionError instanceof Error
          ? sessionError.message
          : "Failed to sync the authenticated session.";

      startTransition(() => {
        setBackendUser(null);
        setWorkspace(null);
        setError(message);
      });
    } finally {
      setIsSyncing(false);
    }
  }, [isLoaded, isSignedIn, getToken]);

  useEffect(() => {
    void syncSession();
  }, [syncSession]);

  const value: ScivlySessionContextValue = {
    backendUser,
    error,
    isLoaded,
    isSignedIn: Boolean(isSignedIn),
    isSyncing,
    refresh: async () => {
      await syncSession();
    },
    user: buildUserSnapshot(clerkUser, backendUser),
    workspace,
  };

  return (
    <ScivlySessionContext.Provider value={value}>
      {children}
    </ScivlySessionContext.Provider>
  );
}

export function useScivlySession() {
  const context = useContext(ScivlySessionContext);

  if (!context) {
    throw new Error("useScivlySession must be used within a ScivlySessionProvider");
  }

  return context;
}
