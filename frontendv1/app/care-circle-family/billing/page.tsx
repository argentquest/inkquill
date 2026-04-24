"use client";

import { useLayoutEffect, useState } from "react";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { DataTable } from "@/components/ui/data-table";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { StatCard } from "@/components/ui/stat-card";
import { fetchBillingDashboard } from "@/lib/api";
import type { BillingDashboard } from "@/lib/types";

export default function CareCircleBillingPage() {
  const session = useSession();
  const isOwner = session.user?.is_family_owner === true;

  const [dashboard, setDashboard] = useState<BillingDashboard | null>(null);
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

    fetchBillingDashboard()
      .then((data) => { if (mounted) setDashboard(data); })
      .catch((err) => { if (mounted) setError(err instanceof Error ? err.message : "Unable to load billing."); })
      .finally(() => { if (mounted) setLoading(false); });

    return () => { mounted = false; };
  }, [session.status, isOwner]);

  if (session.status === "loading" || (session.status === "authenticated" && !isOwner)) {
    return <LoadingState label="Checking access" />;
  }

  if (loading) return <LoadingState label="Loading billing" />;
  if (error) return <ErrorState title="Billing could not be loaded." detail={error} />;
  if (!dashboard) return null;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Billing"
        title="Account balance and transactions"
        description="Your Care Circle balance, credit history, and available top-up packages."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          detail={`Currency: ${dashboard.account.currency}`}
          label="Current balance"
          value={dashboard.account.current_balance}
        />
        <StatCard label="Total spent" value={dashboard.account.total_spent} />
        <StatCard label="Credits added" value={dashboard.account.total_credits_added} />
      </div>

      <DataTable
        columns={[
          { key: "type", header: "Type", render: (row) => row.transaction_type },
          { key: "amount", header: "Amount", render: (row) => row.amount },
          { key: "balance", header: "Balance after", render: (row) => row.balance_after },
          { key: "description", header: "Description", render: (row) => row.description ?? "—" },
        ]}
        emptyMessage="No transactions recorded yet."
        rows={dashboard.recent_transactions}
        tableLabel="Transaction history"
      />

      <DataTable
        columns={[
          { key: "name", header: "Package", render: (row) => row.name },
          { key: "credits", header: "Credits", render: (row) => row.credit_amount },
          { key: "price", header: "Price", render: (row) => `$${row.price_usd}` },
          { key: "bonus", header: "Bonus", render: (row) => `${row.bonus_percentage}%` },
        ]}
        emptyMessage="No credit packages are currently available."
        rows={dashboard.available_packages}
        tableLabel="Available credit packages"
      />
    </div>
  );
}
