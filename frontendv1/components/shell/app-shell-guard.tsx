"use client";

import { useLayoutEffect } from "react";
import { usePathname } from "next/navigation";

import { useSession } from "@/components/providers/app-providers";
import { LoadingState } from "@/components/ui/loading-state";
import { getDefaultAuthDestination, resolvePlatformContext } from "@/components/platform/platform-context";

export function AppShellGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const session = useSession();
  const context = resolvePlatformContext(pathname, session);
  const requiresAuth = context.requires_auth;
  const nextPath = pathname && !pathname.startsWith("/auth")
    ? pathname
    : getDefaultAuthDestination(context.surface_id);
  const redirectTarget = `/auth/login?next=${encodeURIComponent(nextPath)}`;

  useLayoutEffect(() => {
    if (!requiresAuth) {
      return;
    }

    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace(redirectTarget);
    }
  }, [redirectTarget, requiresAuth, session.status]);

  if (!requiresAuth) {
    return <>{children}</>;
  }

  if (session.status === "loading") {
    return <LoadingState label="Checking session" />;
  }

  if (session.status === "anonymous" || session.status === "error") {
    return <LoadingState label="Redirecting to login" />;
  }

  return <>{children}</>;
}
