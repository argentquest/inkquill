"use client";

import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "@/components/shell/page-header";
import { DataTable } from "@/components/ui/data-table";
import { DrawerPanel } from "@/components/ui/drawer-panel";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchReferralHistory, fetchReferralRewards, fetchReferralStats } from "@/lib/api";
import type { ReferralHistoryItem, ReferralRewardItem } from "@/lib/types";

export default function ReferralsPage() {
  const statsQuery = useQuery({ queryKey: ["referral-stats"], queryFn: fetchReferralStats });
  const historyQuery = useQuery({ queryKey: ["referral-history"], queryFn: fetchReferralHistory });
  const rewardsQuery = useQuery({ queryKey: ["referral-rewards"], queryFn: fetchReferralRewards });

  if (statsQuery.isLoading || historyQuery.isLoading || rewardsQuery.isLoading) {
    return <LoadingState label="Loading referral activity" />;
  }

  if (statsQuery.isError || historyQuery.isError || rewardsQuery.isError || !statsQuery.data || !historyQuery.data || !rewardsQuery.data) {
    const firstError = statsQuery.error ?? historyQuery.error ?? rewardsQuery.error;
    return (
      <ErrorState
        detail={firstError instanceof Error ? firstError.message : undefined}
        onRetry={() => {
          void statsQuery.refetch();
          void historyQuery.refetch();
          void rewardsQuery.refetch();
        }}
        retryLabel="Reload referrals"
        title="Referral data could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        description="Sprint 3 moves referrals out of the far-future backlog and into the shared commercial framework so the route contract, loading states, and data presentation are stable early."
        eyebrow="Referrals"
        title="Track invitations, conversions, and earned coins from one route."
      />

      <section className="grid gap-5 md:grid-cols-3">
        <StatCard label="Total referrals" value={String(statsQuery.data.total_referrals)} />
        <StatCard label="Converted" value={String(statsQuery.data.converted_referrals)} />
        <StatCard label="Coins earned" value={String(statsQuery.data.total_coins_earned)} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-6">
          <DataTable<ReferralHistoryItem>
            columns={[
              { key: "platform", header: "Platform", render: (row) => row.source_platform ?? "Direct" },
              { key: "content", header: "Content", render: (row) => row.source_content_type ?? "General" },
              { key: "conversion", header: "Converted", render: (row) => (row.is_converted ? "Yes" : "No") },
              { key: "created", header: "Tracked", render: (row) => new Date(row.created_at).toLocaleDateString() }
            ]}
            emptyMessage="No referral visits have been tracked yet."
            rows={historyQuery.data.referrals}
            tableLabel="Referral history"
          />

          <DataTable<ReferralRewardItem>
            columns={[
              { key: "rewardType", header: "Reward Type", render: (row) => row.reward_type },
              { key: "coins", header: "Coins", render: (row) => String(row.coin_amount) },
              { key: "awarded", header: "Awarded", render: (row) => new Date(row.awarded_at).toLocaleDateString() }
            ]}
            emptyMessage="No referral rewards have been awarded yet."
            rows={rewardsQuery.data.rewards}
            tableLabel="Referral rewards"
          />
        </div>

        <DrawerPanel
          description="The route also establishes a reusable side-panel pattern for contextual metrics and platform breakdowns."
          title="Referral overview"
        >
          <div className="space-y-4">
            <div className="rounded-[22px] border border-black/10 bg-white/85 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-ink-600">Conversion rate</p>
              <p className="mt-2 font-display text-4xl text-ink-900">{statsQuery.data.conversion_rate}%</p>
            </div>
            <div className="rounded-[22px] border border-black/10 bg-white/85 p-4">
              <p className="text-xs uppercase tracking-[0.22em] text-ink-600">Platform breakdown</p>
              <div className="mt-3 space-y-2 text-sm text-ink-800">
                {Object.entries(statsQuery.data.platform_breakdown).map(([platform, count]) => (
                  <div className="flex items-center justify-between" key={platform}>
                    <span>{platform}</span>
                    <span>{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </DrawerPanel>
      </section>
    </div>
  );
}
