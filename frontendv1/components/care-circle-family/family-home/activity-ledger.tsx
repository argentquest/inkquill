"use client";

import { ProvBadge } from "@/components/care-circle-family/prov-badge";

export interface LedgerEvent {
  time: string;
  entry: string;
  tag: "family" | "curated" | "auto";
}

export function ActivityLedger({
  events,
}: {
  events?: LedgerEvent[] | null;
}) {
  if (!events || events.length === 0) return null;

  return (
    <div className="rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel">
      <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-600">
        Activity Ledger
      </h3>
      <div className="mt-4 space-y-0">
        {events.map((e, i) => (
          <div
            key={i}
            className="flex items-baseline gap-4 border-b border-dashed border-ink-900/10 py-3 last:border-b-0"
          >
            <span className="w-16 shrink-0 text-xs font-semibold text-ink-400">
              {e.time}
            </span>
            <span className="flex-1 text-sm text-ink-900">{e.entry}</span>
            <ProvBadge kind={e.tag}>
              {e.tag === "family"
                ? "Family"
                : e.tag === "curated"
                  ? "Curated"
                  : "Auto"}
            </ProvBadge>
          </div>
        ))}
      </div>
    </div>
  );
}
