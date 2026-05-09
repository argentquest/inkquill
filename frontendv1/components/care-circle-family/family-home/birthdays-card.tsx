"use client";

import { Cake } from "lucide-react";

export function BirthdaysCard({
  items,
}: {
  items?: { name: string; date: string; age?: number }[] | null;
}) {
  if (!items || items.length === 0) return null;

  return (
    <div className="rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white">
      <div className="flex items-center gap-2">
        <Cake className="h-4 w-4 text-ember" />
        <span className="text-sm font-semibold text-ink-900">Birthdays</span>
      </div>
      <ul className="mt-3 space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-baseline justify-between text-sm">
            <span className="text-ink-900">{item.name}</span>
            <span className="text-xs text-ink-400">
              {item.date}
              {item.age ? ` · ${item.age}` : ""}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
