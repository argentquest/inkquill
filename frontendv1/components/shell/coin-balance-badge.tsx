"use client";

import { Coins } from "lucide-react";

import { useBalance } from "@/components/providers/app-providers";

export function CoinBalanceBadge() {
  const { balance, currency, error, loading, refreshBalance } = useBalance();

  return (
    <button
      className="inline-flex items-center gap-2 rounded-full border border-forest/15 bg-forest px-4 py-2 text-sm text-paper transition hover:bg-forest/90"
      onClick={() => void refreshBalance()}
      type="button"
    >
      <Coins className="h-4 w-4" />
      <span>{loading ? "Loading balance" : `${balance.toFixed(2)} ${currency}`}</span>
      {error ? <span className="hidden text-xs opacity-70 md:inline">retry</span> : null}
    </button>
  );
}
