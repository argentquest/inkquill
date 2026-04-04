"use client";

import Link from "next/link";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { AccountSummaryPanel } from "@/components/ui/account-summary-panel";

export function StorytellingAccountWorkspace() {
  const { user } = useSession();

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Storytelling account"
        title="Account shell for the storytelling workspace."
        description="The shared platform resolves authenticated storytelling users into an app-specific account surface instead of the legacy shared /app shell."
        action={
          <Link
            className="inline-flex min-w-[160px] items-center justify-center rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
            href="/storytelling/account/edit"
          >
            Edit profile
          </Link>
        }
      />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <AccountSummaryPanel user={user} />
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
          <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Workspace scope</p>
          <h2 className="mt-3 font-display text-3xl text-ink-900">Storytelling stays user-owned.</h2>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            Billing, profile changes, and authoring access all resolve against the storytelling surface, not the retired shared dashboard shell.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link className="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700" href="/storytelling/billing">
              Review billing
            </Link>
            <Link className="rounded-full border border-black/10 bg-white/70 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white" href="/storytelling/referrals">
              Open referrals
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
