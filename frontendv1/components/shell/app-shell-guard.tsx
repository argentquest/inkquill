"use client";

import { useLayoutEffect } from "react";
import { usePathname } from "next/navigation";

import { useSession } from "@/components/providers/app-providers";
import { LoadingState } from "@/components/ui/loading-state";

export function AppShellGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { status } = useSession();

  useLayoutEffect(() => {
    if (status === "anonymous") {
      const next = encodeURIComponent(pathname || "/app/account");
      window.location.replace(`/auth/login?next=${next}`);
    }
  }, [pathname, status]);

  if (status === "loading") {
    return <LoadingState label="Checking session" />;
  }

  if (status === "anonymous") {
    return <LoadingState label="Redirecting to login" />;
  }

  return <>{children}</>;
}
