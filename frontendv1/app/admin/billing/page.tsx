"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DollarSign, Loader2, Minus, Plus, TrendingUp } from "lucide-react";
import { useLayoutEffect, useState } from "react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { LoadingState } from "@/components/ui/loading-state";
import { adminAdjustCredits, adminFetchFamilies, fetchAdminBillingDashboard } from "@/lib/api";

const INPUT_CLS =
  "rounded-[16px] border border-black/10 bg-[#fcfaf6] px-4 py-2.5 text-base text-ink-900 outline-none focus:border-amber-600 w-full";
const LABEL_CLS = "text-sm uppercase tracking-[0.18em] text-ink-600 font-medium";

export default function AdminBillingPage() {
  const session = useSession();
  const isAdmin = session.user?.is_admin === true;
  const queryClient = useQueryClient();

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

  const { data: families = [] } = useQuery({
    queryKey: ["admin-families"],
    queryFn: adminFetchFamilies,
    enabled: isAdmin,
  });

  const [selectedFamilyId, setSelectedFamilyId] = useState<string>("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [adjustDone, setAdjustDone] = useState(false);

  const selectedFamily = families.find((f) => String(f.id) === selectedFamilyId) ?? null;

  const { mutate: adjust, isPending: adjusting, isError: adjustError } = useMutation({
    mutationFn: (coins: number) => {
      if (!selectedFamily?.owner_user_id) throw new Error("No owner");
      return adminAdjustCredits(selectedFamily.owner_user_id, coins, description);
    },
    onSuccess: () => {
      setAmount("");
      setDescription("");
      setAdjustDone(true);
      queryClient.invalidateQueries({ queryKey: ["admin-billing-dashboard"] });
    },
  });

  const parsedAmount = Number(amount);
  const canSubmit =
    selectedFamily?.owner_user_id != null &&
    !isNaN(parsedAmount) &&
    parsedAmount !== 0 &&
    description.trim().length > 0;

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

      {/* ── Family Credit Adjustment ─────────────────────────── */}
      <div className="rounded-[24px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <h2 className="mb-1 font-semibold text-ink-900">Family Credit Adjustment</h2>
        <p className="mb-6 text-sm text-ink-600">
          Select a family, enter a coin amount (positive to add, negative to remove), and a reason.
        </p>

        <form
          className="space-y-5"
          onSubmit={(e) => {
            e.preventDefault();
            if (canSubmit) {
              setAdjustDone(false);
              adjust(parsedAmount);
            }
          }}
        >
          {/* Family selector */}
          <div className="flex flex-col gap-1.5">
            <label className={LABEL_CLS} htmlFor="adjust-family">Family</label>
            <select
              className={INPUT_CLS}
              data-testid="adjust-family"
              id="adjust-family"
              value={selectedFamilyId}
              onChange={(e) => { setSelectedFamilyId(e.target.value); setAdjustDone(false); }}
            >
              <option value="">— Select a family —</option>
              {families.map((f) => (
                <option key={f.id} value={String(f.id)}>
                  {f.name}
                  {f.owner_display_name ? ` · ${f.owner_display_name}` : f.owner_username ? ` · ${f.owner_username}` : ""}
                  {f.is_disabled ? " (disabled)" : ""}
                </option>
              ))}
            </select>
            {selectedFamily && (
              <p className="text-sm text-ink-500">
                Owner:{" "}
                <span className="font-medium text-ink-700">
                  {selectedFamily.owner_display_name ?? selectedFamily.owner_username ?? "unknown"}
                </span>
                {selectedFamily.owner_user_id == null && (
                  <span className="ml-2 text-amber-600">(no owner account — cannot adjust)</span>
                )}
              </p>
            )}
          </div>

          {/* Amount + quick buttons */}
          <div className="flex flex-col gap-1.5">
            <label className={LABEL_CLS} htmlFor="adjust-amount">Amount (coins)</label>
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                {[-500, -100, -10].map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setAmount(String(n))}
                    className="flex items-center gap-0.5 rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-sm font-medium text-red-700 transition hover:bg-red-100"
                  >
                    <Minus className="size-3" />{Math.abs(n)}
                  </button>
                ))}
              </div>
              <input
                className={INPUT_CLS}
                data-testid="adjust-amount"
                id="adjust-amount"
                onChange={(e) => setAmount(e.target.value)}
                placeholder="e.g. 500 or -100"
                type="number"
                value={amount}
              />
              <div className="flex gap-1">
                {[10, 100, 500].map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setAmount(String(n))}
                    className="flex items-center gap-0.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-sm font-medium text-emerald-700 transition hover:bg-emerald-100"
                  >
                    <Plus className="size-3" />{n}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="flex flex-col gap-1.5">
            <label className={LABEL_CLS} htmlFor="adjust-desc">Reason</label>
            <input
              className={INPUT_CLS}
              data-testid="adjust-desc"
              id="adjust-desc"
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g. Promotional credit, refund for billing error"
              type="text"
              value={description}
            />
          </div>

          <div className="flex items-center gap-4">
            <Button
              className="gap-2"
              disabled={adjusting || !canSubmit}
              type="submit"
            >
              {adjusting ? <Loader2 className="size-4 animate-spin" /> : <DollarSign className="size-4" />}
              {parsedAmount < 0 ? "Remove credits" : "Add credits"}
            </Button>
            {parsedAmount !== 0 && canSubmit && (
              <p className="text-sm text-ink-600">
                {parsedAmount > 0 ? "+" : ""}{parsedAmount.toLocaleString()} coins →{" "}
                <span className="font-medium text-ink-900">
                  {selectedFamily?.owner_display_name ?? selectedFamily?.owner_username}
                </span>
              </p>
            )}
          </div>
        </form>

        {adjustError && (
          <p className="mt-4 text-sm text-red-600" data-testid="adjust-error">Failed to adjust credits. Check that this family has an owner account.</p>
        )}
        {adjustDone && (
          <p className="mt-4 text-sm text-emerald-600" data-testid="adjust-success">
            Credits adjusted successfully.
          </p>
        )}
      </div>
    </div>
  );
}
