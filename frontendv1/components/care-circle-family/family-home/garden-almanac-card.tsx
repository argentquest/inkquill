"use client";

import { Sprout } from "lucide-react";
import { ProvBadge } from "@/components/care-circle-family/prov-badge";

export function GardenAlmanacCard({
  tip,
}: {
  tip?: { title: string; body: string } | null;
}) {
  if (!tip) return null;

  return (
    <div className="rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sprout className="h-4 w-4 text-forest" />
          <span className="text-sm font-semibold text-ink-900">
            Garden Almanac
          </span>
        </div>
        <ProvBadge kind="auto">Auto</ProvBadge>
      </div>
      <h3 className="mt-3 font-display text-lg font-semibold text-ink-900">
        {tip.title}
      </h3>
      <p className="mt-1 text-sm leading-6 text-ink-600">{tip.body}</p>
    </div>
  );
}
