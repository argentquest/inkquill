"use client";

import { RefreshCcw } from "lucide-react";

import { useBalance, useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { AccountSummaryPanel } from "@/components/ui/account-summary-panel";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";

export default function AccountPage() {
  const { error, refreshSession, status, user } = useSession();
  const balance = useBalance();

  if (status === "loading") {
    return <LoadingState label="Bootstrapping session" />;
  }

  if (error) {
    return (
      <ErrorState
        detail={error}
        onRetry={() => void refreshSession()}
        retryLabel="Reload session"
        title="Account shell could not confirm the current user."
      />
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        action={
          <button
            className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/80 px-4 py-3 text-sm transition hover:border-black/20 hover:bg-white"
            onClick={() => {
              void refreshSession();
              void balance.refreshBalance();
            }}
            type="button"
          >
            <RefreshCcw className="h-4 w-4" />
            Refresh shell data
          </button>
        }
        description="Sprint 2 turns the account route into the stable post-login landing surface, backed by the authenticated shell and the current user profile endpoint."
        eyebrow="Account"
        title={status === "authenticated" && user ? `Welcome back, ${user.display_name ?? user.username}.` : "Account entry"}
      />

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <AccountSummaryPanel user={user} />
        <article className="rounded-[28px] border border-black/10 bg-[linear-gradient(180deg,rgba(31,59,54,0.96),rgba(35,25,19,0.96))] p-6 text-paper shadow-panel">
          <p className="text-xs uppercase tracking-[0.28em] text-paper/70">Coin balance</p>
          <h2 className="mt-3 font-display text-4xl">{balance.loading ? "Loading..." : balance.balance.toFixed(2)}</h2>
          <p className="mt-3 text-sm text-paper/75">{balance.currency}</p>
          <p className="mt-6 text-sm leading-7 text-paper/75">
            The app shell continues to share one balance source across the account landing page and the top navigation.
          </p>
        </article>
      </section>
    </div>
  );
}
