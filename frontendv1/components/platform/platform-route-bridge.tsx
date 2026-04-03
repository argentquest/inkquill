"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { LoadingState } from "@/components/ui/loading-state";
import { getLegacyRouteTarget } from "@/components/platform/platform-context";

export function PlatformRouteBridge() {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    router.replace(getLegacyRouteTarget(pathname));
  }, [pathname, router]);

  return <LoadingState label="Redirecting into the new app surface" />;
}
