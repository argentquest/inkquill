"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/shell/page-header";
import { DataTable } from "@/components/ui/data-table";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchReferralHistory, fetchReferralRewards, fetchReferralStats } from "@/lib/api";
import type { ReferralHistoryResponse, ReferralRewardsResponse, ReferralStats } from "@/lib/types";

export function ReferralsDashboardRoute() {
  const [stats, setStats] = useState<ReferralStats | null>(null);
  const [history, setHistory] = useState<ReferralHistoryResponse | null>(null);
  const [rewards, setRewards] = useState<ReferralRewardsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [statsPayload, historyPayload, rewardsPayload] = await Promise.all([
          fetchReferralStats(),
          fetchReferralHistory(),
          fetchReferralRewards()
        ]);
        if (mounted) {
          setStats(statsPayload);
          setHistory(historyPayload);
          setRewards(rewardsPayload);
        }
      } catch (loadError) {
        if (mounted) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load referral data.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Referrals"
        title="Track invitations, conversions, and earned coins from one route."
        description="Referral performance remains visible inside the storytelling surface while the underlying ownership and reward contracts stay shared-platform aware."
      />
      {loading ? <LoadingState label="Loading referrals" /> : null}
      {!loading && error ? <ErrorState title="Referral data could not be loaded." detail={error} /> : null}
      {!loading && !error && stats && history && rewards ? (
        <>
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard label="Total referrals" value={`${stats.total_referrals}`} />
            <StatCard label="Converted referrals" value={`${stats.converted_referrals}`} />
            <StatCard label="Conversion rate" value={`${stats.conversion_rate}%`} />
            <StatCard label="Coins earned" value={`${stats.total_coins_earned}`} />
          </div>
          <DataTable
            columns={[
              { key: "source", header: "Source", render: (row) => row.source_platform ?? "direct" },
              { key: "content", header: "Content", render: (row) => row.source_content_type ?? "workspace" },
              { key: "converted", header: "Converted", render: (row) => (row.is_converted ? "Yes" : "No") },
              { key: "created", header: "Created", render: (row) => new Date(row.created_at).toLocaleDateString() }
            ]}
            emptyMessage="No referral history recorded yet."
            rows={history.referrals}
            tableLabel="Referral history"
          />
          <DataTable
            columns={[
              { key: "rewardType", header: "Reward type", render: (row) => row.reward_type },
              { key: "amount", header: "Coins", render: (row) => `${row.coin_amount}` },
              { key: "awarded", header: "Awarded", render: (row) => new Date(row.awarded_at).toLocaleDateString() }
            ]}
            emptyMessage="No rewards have been awarded yet."
            rows={rewards.rewards}
            tableLabel="Referral rewards"
          />
        </>
      ) : null}
    </div>
  );
}
