"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { DollarSign, Loader2, TrendingUp } from "lucide-react";
import { useLayoutEffect, useState } from "react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { adminAdjustCredits, fetchAdminBillingDashboard } from "@/lib/api";

export default function AdminBillingPage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;

  useLayoutEffect(() => {
    if (session.status === "anonymous" || session.status === "error") {
      window.location.replace("/auth/login?next=/admin/billing");
    } else if (session.status === "authenticated" && !isAdmin) {
      window.location.replace("/access-denied?surface=admin");
    }
  }, [session.status, isAdmin]);

  const { data: dashboard, isLoading, isError } = useQuery({
    queryKey: ["admin-billing-dashboard"],
    queryFn: fetchAdminBillingDashboard,
    enabled: isAdmin,
  });

  const [adjustUserId, setAdjustUserId] = useState("");
  const [adjustAmount, setAdjustAmount] = useState("");
  const [adjustDesc, setAdjustDesc] = useState("");
  const [adjustDone, setAdjustDone] = useState(false);

  const { mutate: adjust, isPending: adjusting, isError: adjustError } = useMutation({
    mutationFn: () =>
      adminAdjustCredits(Number(adjustUserId), Number(adjustAmount), adjustDesc),
    onSuccess: () => {
      setAdjustUserId("");
      setAdjustAmount("");
      setAdjustDesc("");
      setAdjustDone(true);
    },
  });

  if (session.status === "loading" || (session.status === "authenticated" && !isAdmin)) {
    return <LoadingState label="Checking access" />;
  }

  const stats = dashboard?.system_stats as Record<string, unknown> | undefined;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Admin › Billing"
        title="Billing Dashboard"
        description="System-wide billing statistics, recent transactions, and manual credit adjustment."
      />

      {isLoading ? (
        <div className="flex items-center gap-2 text-sm text-ink-500">
          <Loader2 className="size-4 animate-spin" /> Loading dashboard…
        </div>
      ) : isError ? (
        <p className="text-sm text-red-600" data-testid="billing-error">Failed to load billing dashboard.</p>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3" data-testid="billing-stats">
            {stats
              ? Object.entries(stats).map(([key, value]) => (
                  <div
                    key={key}
                    className="rounded-[20px] border border-black/10 bg-white/70 p-5 shadow-panel"
                    data-testid="billing-stat-card"
                  >
                    <p className="text-xs uppercase tracking-[0.2em] text-ink-500">{key.replace(/_/g, " ")}</p>
                    <p className="mt-2 text-2xl font-semibold text-ink-900">
                      {typeof value === "number" ? value.toLocaleString() : String(value ?? "—")}
                    </p>
                  </div>
                ))
              : (
                <div className="col-span-3 flex items-center gap-2 text-sm text-ink-500">
                  <TrendingUp className="size-4" /> No stats available.
                </div>
              )}
          </div>

          <div className="rounded-[24px] border border-black/10 bg-white/70 p-6 shadow-panel">
            <h2 className="mb-4 font-semibold text-ink-900">Recent Transactions</h2>
            {(dashboard?.recent_transactions ?? []).length === 0 ? (
              <p className="text-sm text-ink-500" data-testid="transactions-empty">No recent transactions.</p>
            ) : (
              <ul className="space-y-2" data-testid="transactions-list">
                {(dashboard?.recent_transactions as Record<string, unknown>[]).map((tx, i) => (
                  <li
                    key={i}
                    className="flex items-center justify-between rounded-2xl border border-black/5 bg-white px-4 py-3 text-sm"
                    data-testid="transaction-row"
                  >
                    <span className="text-ink-700">{String(tx.description ?? tx.type ?? "Transaction")}</span>
                    <span className="font-semibold text-ink-900">{String(tx.amount ?? "—")}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}

      <div className="rounded-[24px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <h2 className="mb-1 font-semibold text-ink-900">Manual Credit Adjustment</h2>
        <p className="mb-5 text-sm text-ink-600">Directly add or subtract coins from any user account.</p>
        <form
          className="flex flex-col gap-4 sm:flex-row sm:items-end"
          onSubmit={(e) => { e.preventDefault(); adjust(); }}
        >
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-[0.2em] text-ink-600" htmlFor="adjust-user">
              User ID
            </label>
            <input
              className="rounded-[16px] border border-black/10 bg-[#fcfaf6] px-4 py-2.5 text-sm text-ink-900 outline-none focus:border-amber-600"
              data-testid="adjust-user-id"
              id="adjust-user"
              min={1}
              onChange={(e) => setAdjustUserId(e.target.value)}
              placeholder="42"
              type="number"
              value={adjustUserId}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs uppercase tracking-[0.2em] text-ink-600" htmlFor="adjust-amount">
              Amount (coins)
            </label>
            <input
              className="rounded-[16px] border border-black/10 bg-[#fcfaf6] px-4 py-2.5 text-sm text-ink-900 outline-none focus:border-amber-600"
              data-testid="adjust-amount"
              id="adjust-amount"
              onChange={(e) => setAdjustAmount(e.target.value)}
              placeholder="-100 or 500"
              type="number"
              value={adjustAmount}
            />
          </div>
          <div className="flex flex-1 flex-col gap-1">
            <label className="text-xs uppercase tracking-[0.2em] text-ink-600" htmlFor="adjust-desc">
              Description
            </label>
            <input
              className="rounded-[16px] border border-black/10 bg-[#fcfaf6] px-4 py-2.5 text-sm text-ink-900 outline-none focus:border-amber-600"
              data-testid="adjust-desc"
              id="adjust-desc"
              onChange={(e) => setAdjustDesc(e.target.value)}
              placeholder="Refund for billing error"
              type="text"
              value={adjustDesc}
            />
          </div>
          <Button
            className="gap-2 shrink-0"
            disabled={adjusting || !adjustUserId || !adjustAmount || !adjustDesc}
            type="submit"
          >
            {adjusting ? <Loader2 className="size-4 animate-spin" /> : <DollarSign className="size-4" />}
            Adjust credits
          </Button>
        </form>
        {adjustError && (
          <p className="mt-3 text-sm text-red-600" data-testid="adjust-error">Failed to adjust credits.</p>
        )}
        {adjustDone && (
          <p className="mt-3 text-sm text-emerald-600" data-testid="adjust-success">Credits adjusted successfully.</p>
        )}
      </div>
    </div>
  );
}
