"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/shell/page-header";
import { DataTable } from "@/components/ui/data-table";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchBillingDashboard } from "@/lib/api";
import type { BillingDashboard } from "@/lib/types";

export function BillingDashboardRoute() {
  const [dashboard, setDashboard] = useState<BillingDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const payload = await fetchBillingDashboard();
        if (mounted) {
          setDashboard(payload);
        }
      } catch (loadError) {
        if (mounted) {
          setError(loadError instanceof Error ? loadError.message : "Unable to load billing dashboard.");
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
        eyebrow="Billing"
        title="Your balance, packages, and transaction history live in one route."
        description="Storytelling billing stays route-local so the shared platform can support user-owned and family-owned billing surfaces without mixing their contracts."
      />
      {loading ? <LoadingState label="Loading billing" /> : null}
      {!loading && error ? <ErrorState title="Billing data could not be loaded." detail={error} /> : null}
      {!loading && !error && dashboard ? (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            <StatCard detail={`Currency: ${dashboard.account.currency}`} label="Current balance" value={dashboard.account.current_balance} />
            <StatCard label="Total spent" value={dashboard.account.total_spent} />
            <StatCard label="Credits added" value={dashboard.account.total_credits_added} />
          </div>
          <DataTable
            columns={[
              { key: "type", header: "Type", render: (row) => row.transaction_type },
              { key: "amount", header: "Amount", render: (row) => row.amount },
              { key: "balance", header: "Balance after", render: (row) => row.balance_after },
              { key: "description", header: "Description", render: (row) => row.description ?? "No description" }
            ]}
            emptyMessage="No billing transactions recorded yet."
            rows={dashboard.recent_transactions}
            tableLabel="Billing transactions"
          />
          <DataTable
            columns={[
              { key: "name", header: "Package", render: (row) => row.name },
              { key: "credits", header: "Credits", render: (row) => row.credit_amount },
              { key: "price", header: "Price", render: (row) => `$${row.price_usd}` },
              { key: "bonus", header: "Bonus", render: (row) => `${row.bonus_percentage}%` }
            ]}
            emptyMessage="No credit packages are currently available."
            rows={dashboard.available_packages}
            tableLabel="Available credit packages"
          />
        </>
      ) : null}
    </div>
  );
}
