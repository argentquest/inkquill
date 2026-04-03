import Link from "next/link";

import { PublicShell } from "@/components/shell/public-shell";
import { PageHeader } from "@/components/shell/page-header";

export default function AccessDeniedPage() {
  return (
    <PublicShell>
      <PageHeader
        action={
          <Link className="inline-flex items-center rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700" href="/auth/login">
            Return to sign in
          </Link>
        }
        description="The shared platform uses this route when an authenticated user resolves into the wrong application surface or lacks the required membership."
        eyebrow="Access Denied"
        title="This application surface is not available for the current account."
      />
      <section className="mt-8 rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <p className="text-sm leading-7 text-ink-700">
          Route protection, app membership, and app-aware redirects should fail explicitly instead of dropping users into the wrong product surface.
        </p>
      </section>
    </PublicShell>
  );
}
