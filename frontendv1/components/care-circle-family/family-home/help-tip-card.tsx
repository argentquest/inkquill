"use client";

import Link from "next/link";
import { Lightbulb } from "lucide-react";

export function HelpTipCard({
  tip,
}: {
  tip?: { title: string; href: string } | null;
}) {
  if (!tip) return null;

  return (
    <Link
      href={tip.href}
      className="group block rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white"
    >
      <div className="flex items-center gap-2">
        <Lightbulb className="h-4 w-4 text-ember" />
        <span className="text-xs font-semibold uppercase tracking-wider text-ink-400">
          Tip
        </span>
      </div>
      <h3 className="mt-3 font-display text-lg font-semibold text-ink-900 group-hover:text-ember">
        {tip.title}
      </h3>
    </Link>
  );
}
