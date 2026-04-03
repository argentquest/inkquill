"use client";

import { useQuery } from "@tanstack/react-query";

import { PageHeader } from "@/components/shell/page-header";
import { DataTable } from "@/components/ui/data-table";
import { DrawerPanel } from "@/components/ui/drawer-panel";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchBillingDashboard } from "@/lib/api";
import type { BillingTransaction, CreditPackage } from "@/lib/types";

export default function BillingPage() {
  const billingQuery = useQuery({
    queryKey: ["billing-dashboard"],
    queryFn: fetchBillingDashboard
  });

  if (billingQuery.isLoading) {
    return <LoadingState label="Loading billing dashboard" />;
  }

  if (billingQuery.isError || !billingQuery.data) {
    return (
      <ErrorState
        detail={billingQuery.error instanceof Error ? billingQuery.error.message : undefined}
        onRetry={() => void billingQuery.refetch()}
        retryLabel="Reload billing"
        title="Billing data could not be loaded."
      />
    );
  }

  const { account, available_packages, recent_transactions } = billingQuery.data;

  return (
    <div className="space-y-8">
      <PageHeader
        description="Billing becomes a first-class framework route in Sprint 3: authenticated, shell-aware, and backed by the same API/query conventions future commercial pages will reuse."
        eyebrow="Billing"
        title="Your balance, packages, and transaction history live in one route."
      />

      <section className="grid gap-5 md:grid-cols-3">
        <StatCard detail={`All values remain in ${account.currency}.`} label="Current balance" value={account.current_balance} />
        <StatCard label="Credits added" value={account.total_credits_added} />
        <StatCard label="Total spent" value={account.total_spent} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-6">
          <DataTable<BillingTransaction>
            columns={[
              { key: "type", header: "Type", render: (row) => row.transaction_type.replaceAll("_", " ") },
              { key: "amount", header: "Amount", render: (row) => row.amount },
              { key: "balance", header: "Balance After", render: (row) => row.balance_after },
              { key: "description", header: "Description", render: (row) => row.description ?? "No description" }
            ]}
            emptyMessage="No transactions are available yet."
            rows={recent_transactions}
            tableLabel="Billing transactions"
          />
        </div>

        <DrawerPanel
          description="Packages remain backend-driven, but this route now provides the framework surface, loading state, and stable display pattern."
          title="Available packages"
        >
          {available_packages.length === 0 ? (
            <EmptyState
              description="No packages are active right now."
              eyebrow="Packages"
              title="Nothing to purchase yet."
            />
          ) : (
            <div className="space-y-4">
              {available_packages.map((item: CreditPackage) => (
                <article className="rounded-[22px] border border-black/10 bg-white/85 p-4" key={item.id}>
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <h2 className="font-display text-2xl text-ink-900">{item.name}</h2>
                      <p className="mt-2 text-sm leading-7 text-ink-700">{item.description ?? "Credit package"}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm uppercase tracking-[0.22em] text-ink-600">Credits</p>
                      <p className="mt-1 text-2xl text-ink-900">{item.credit_amount}</p>
                    </div>
                  </div>
                  <p className="mt-4 text-sm text-ink-700">
                    ${item.price_usd} USD
                    {item.bonus_percentage !== "0" && item.bonus_percentage !== "0.00" ? ` + ${item.bonus_percentage}% bonus` : ""}
                  </p>
                </article>
              ))}
            </div>
          )}
        </DrawerPanel>
      </section>
    </div>
  );
}
