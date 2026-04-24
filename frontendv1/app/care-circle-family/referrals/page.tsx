"use client";

import { useLayoutEffect, useState } from "react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { DataTable } from "@/components/ui/data-table";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchReferralHistory, fetchReferralRewards, fetchReferralStats } from "@/lib/api";
import type { ReferralHistoryResponse, ReferralRewardsResponse, ReferralStats } from "@/lib/types";

export default function CareCircleReferralsPage() {
  const session = useSession();
  const isOwner = session.user?.is_family_owner === true;

  const [stats, setStats] = useState<ReferralStats | null>(null);
  const [history, setHistory] = useState<ReferralHistoryResponse | null>(null);
  const [rewards, setRewards] = useState<ReferralRewardsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useLayoutEffect(() => {
    if (session.status === "authenticated" && !isOwner) {
      window.location.replace("/care-circle-family");
    }
  }, [session.status, isOwner]);

  useLayoutEffect(() => {
    if (session.status !== "authenticated" || !isOwner) return;

    let mounted = true;
    setLoading(true);
    setError(null);

    Promise.all([fetchReferralStats(), fetchReferralHistory(), fetchReferralRewards()])
      .then(([s, h, r]) => {
        if (!mounted) return;
        setStats(s);
        setHistory(h);
        setRewards(r);
      })
      .catch((err) => { if (mounted) setError(err instanceof Error ? err.message : "Unable to load referral data."); })
      .finally(() => { if (mounted) setLoading(false); });

    return () => { mounted = false; };
  }, [session.status, isOwner]);

  if (session.status === "loading" || (session.status === "authenticated" && !isOwner)) {
    return <LoadingState label="Checking access" />;
  }

  if (loading) return <LoadingState label="Loading referrals" />;
  if (error) return <ErrorState title="Referral data could not be loaded." detail={error} />;
  if (!stats || !history || !rewards) return null;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Referrals"
        title="Invitations, conversions, and earned credits"
        description="Share your Care Circle referral link to earn credits toward your family's newsletter delivery."
      />
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Total referrals" value={`${stats.total_referrals}`} />
        <StatCard label="Converted" value={`${stats.converted_referrals}`} />
        <StatCard label="Conversion rate" value={`${stats.conversion_rate}%`} />
        <StatCard label="Credits earned" value={`${stats.total_coins_earned}`} />
      </div>
      {stats.referral_url && (
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
          <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Your referral link</p>
          <p className="mt-3 font-mono text-sm text-ink-900 break-all">{stats.referral_url}</p>
        </section>
      )}
      <DataTable
        columns={[
          { key: "source", header: "Source", render: (row) => row.source_platform ?? "direct" },
          { key: "content", header: "Content", render: (row) => row.source_content_type ?? "—" },
          { key: "converted", header: "Converted", render: (row) => (row.is_converted ? "Yes" : "No") },
          { key: "created", header: "Date", render: (row) => new Date(row.created_at).toLocaleDateString() },
        ]}
        emptyMessage="No referral history recorded yet."
        rows={history.referrals}
        tableLabel="Referral history"
      />
      <DataTable
        columns={[
          { key: "type", header: "Reward type", render: (row) => row.reward_type },
          { key: "amount", header: "Credits", render: (row) => `${row.coin_amount}` },
          { key: "awarded", header: "Awarded", render: (row) => new Date(row.awarded_at).toLocaleDateString() },
        ]}
        emptyMessage="No rewards have been awarded yet."
        rows={rewards.rewards}
        tableLabel="Referral rewards"
      />
    </div>
  );
}
