"use client";

import { usePathname } from "next/navigation";

import { useSession } from "@/components/providers/app-providers";
import { AppMembershipGuard } from "@/components/platform/app-membership-guard";
import { resolvePlatformContext } from "@/components/platform/platform-context";
import { AppShellGuard } from "@/components/shell/app-shell-guard";

export function PlatformAppGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const session = useSession();
  const context = resolvePlatformContext(pathname, session);

  if (context.requires_auth) {
    return (
      <AppShellGuard>
        <AppMembershipGuard>{children}</AppMembershipGuard>
      </AppShellGuard>
    );
  }

  return <AppMembershipGuard>{children}</AppMembershipGuard>;
}
