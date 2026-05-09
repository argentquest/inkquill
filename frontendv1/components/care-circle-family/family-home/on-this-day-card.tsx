"use client";

import { ProvBadge } from "@/components/care-circle-family/prov-badge";

export function OnThisDayCard({
  event,
}: {
  event?: { year: string; title: string; description?: string } | null;
}) {
  if (!event) return null;

  return (
    <div className="rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white">
      <ProvBadge kind="curated">On this day · {event.year}</ProvBadge>
      <h3 className="mt-3 font-display text-lg font-semibold text-ink-900">
        {event.title}
      </h3>
      {event.description && (
        <p className="mt-1 text-sm leading-6 text-ink-600">
          {event.description}
        </p>
      )}
    </div>
  );
}
