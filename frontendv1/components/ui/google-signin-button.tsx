"use client";

import { Chrome } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { getGoogleSignInUrl } from "@/lib/api";

export function GoogleSigninButton() {
  const session = useSession();
  const isAdmin = session.status === "authenticated" && session.user?.is_admin === true;

  if (!isAdmin) {
    return null;
  }

  return (
    <a
      className="inline-flex w-full items-center justify-center gap-3 rounded-full border border-black/10 bg-white/85 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white"
      href={getGoogleSignInUrl()}
    >
      <Chrome className="h-4 w-4" />
      Continue with Google
    </a>
  );
}
