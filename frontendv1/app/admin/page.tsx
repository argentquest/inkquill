"use client";

import { useLayoutEffect } from "react";

import { useSession } from "@/components/providers/app-providers";
import { LoadingState } from "@/components/ui/loading-state";

export default function AdminRedirectPage() {
  const session = useSession();

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace(`/auth/login?next=/care-circle-family/admin`);
    } else if (session.status === "authenticated") {
      if (session.user?.is_admin) {
        window.location.replace("/care-circle-family/admin");
      } else {
        window.location.replace("/access-denied?surface=care-circle-family");
      }
    }
  }, [session.status, session.user?.is_admin]);

  if (session.status === "loading") {
    return <LoadingState label="Checking session" />;
  }

  return <LoadingState label="Redirecting" />;
}
