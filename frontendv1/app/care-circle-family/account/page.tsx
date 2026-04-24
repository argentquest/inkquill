"use client";

import Link from "next/link";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { AccountSummaryPanel } from "@/components/ui/account-summary-panel";

export default function CareCircleAccountPage() {
  const { user } = useSession();
  const isOwner = user?.is_family_owner === true;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Account"
        title="Your Care Circle account"
        description="Manage your profile, billing, and referrals from here."
        action={
          <Link
            className="inline-flex min-w-[160px] items-center justify-center rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
            href="/care-circle-family/account/edit"
          >
            Edit profile
          </Link>
        }
      />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <AccountSummaryPanel user={user} />
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
          <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Family scope</p>
          <h2 className="mt-3 font-display text-3xl text-ink-900">
            {isOwner ? "You own this Care Circle." : "You are a member of this Care Circle."}
          </h2>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            {isOwner
              ? "As the family owner you manage billing, credits, and referrals for the whole circle."
              : "Family members can view and manage friend profiles but billing and referrals are handled by the family owner."}
          </p>
          {isOwner && (
            <div className="mt-6 flex flex-wrap gap-3">
              <Link
                className="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
                href="/care-circle-family/billing"
              >
                Review billing
              </Link>
              <Link
                className="rounded-full border border-black/10 bg-white/70 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white"
                href="/care-circle-family/referrals"
              >
                Open referrals
              </Link>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
