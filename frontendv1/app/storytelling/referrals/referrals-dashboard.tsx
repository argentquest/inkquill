"use client";

import { useEffect, useState } from "react";
import { Copy, Gift, Users } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { DataTable } from "@/components/ui/data-table";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchReferralHistory, fetchReferralRewards, fetchReferralStats } from "@/lib/api";
import type { ReferralHistoryResponse, ReferralRewardsResponse, ReferralStats } from "@/lib/types";

function ReferralIntroPanel({ stats }: { stats: ReferralStats }) {
  const [copied, setCopied] = useState(false);
  const url = stats.referral_url ?? "";
  const code = stats.referral_code ?? "";

  function copy() {
    if (!url) return;
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => undefined);
  }

  return (
    <div className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-sm" data-testid="referral-intro-panel">
      <div className="flex flex-wrap items-start gap-8">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-amber-50 text-amber-600">
            <Gift className="size-6" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-ink-900">Invite friends, earn coins</h2>
            <p className="mt-1 max-w-xs text-sm text-ink-500">
              Share your referral link. When a friend signs up and activates their account, you both receive coins to spend on AI generation.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400">
            <Users className="size-6" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-ink-900">How it works</h2>
            <ol className="mt-1 space-y-1 text-sm text-ink-500 list-decimal list-inside">
              <li>Copy your unique referral link below.</li>
              <li>Share it with writers and storytellers.</li>
              <li>When they join and activate, coins are credited to both accounts.</li>
            </ol>
          </div>
        </div>
      </div>

      {url || code ? (
        <div className="mt-6 rounded-2xl border border-black/10 bg-paper px-4 py-3 flex items-center justify-between gap-4">
          <div className="min-w-0">
            <p className="text-xs font-medium text-ink-600 uppercase tracking-wide">Your referral link</p>
            <p className="mt-0.5 truncate text-sm text-ink-900 font-mono" data-testid="referral-url">{url || code}</p>
          </div>
          <button
            className="shrink-0 flex items-center gap-1.5 rounded-full border border-black/10 px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:bg-black/[0.04]"
            data-testid="copy-referral-link"
            onClick={copy}
            type="button"
          >
            <Copy className="size-3" />
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      ) : null}
    </div>
  );
}

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
          <ReferralIntroPanel stats={stats} />
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
