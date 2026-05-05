"use client";

import { useMemo } from "react";
import { usePathname, useSearchParams } from "next/navigation";

import { AppRouteLanding } from "@/components/platform/platform-route-landing";
import { AppShell } from "@/components/shell/app-shell";
import { useSession } from "@/components/providers/app-providers";
import { resolvePlatformContext } from "@/components/platform/platform-context";

export function AppShellResolver({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const session = useSession();
  const context = useMemo(() => resolvePlatformContext(pathname, session), [pathname, session]);
  const showLanding = searchParams.get("surface") !== "minimal";

  return (
    <AppShell>
      <div className="space-y-6">
        {showLanding ? <AppRouteLanding context={context} /> : null}
        {children}
      </div>
    </AppShell>
  );
}
