"use client";

import { useEffect } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { LoadingState } from "@/components/ui/loading-state";
import { useSession } from "@/components/providers/app-providers";
import { resolvePlatformContext } from "@/components/platform/platform-context";

export function AppMembershipGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const session = useSession();
  const context = resolvePlatformContext(pathname, session);
  const forcedDenied = searchParams.get("membership") === "denied";
  const membership = context.memberships.find((item) => item.surface_id === context.surface_id);

  useEffect(() => {
    if (!forcedDenied) {
      return;
    }

    const target = `/access-denied?surface=${encodeURIComponent(context.surface_id)}`;
    router.replace(target);
  }, [context.surface_id, forcedDenied, router]);

  if (session.status === "loading") {
    return <LoadingState label="Resolving platform access" />;
  }

  if (forcedDenied) {
    return <LoadingState label="Redirecting to access policy" />;
  }

  if (context.requires_auth && session.status !== "authenticated") {
    return <>{children}</>;
  }

  if (membership && !membership.granted) {
    return <LoadingState label={membership.reason ?? "Access denied"} />;
  }

  return <>{children}</>;
}
