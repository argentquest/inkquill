"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function NavCard({
  href,
  label,
  description,
  icon: Icon,
  accent = false,
  count,
  members,
}: {
  href: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  accent?: boolean;
  count?: number;
  members?: { name: string; initial: string }[];
}) {
  return (
    <Link
      href={href}
      data-testid={`hub-card-${label.toLowerCase().replace(/\s+/g, "-")}`}
      className={`group relative flex flex-col gap-4 rounded-[24px] border p-5 shadow-panel transition ${
        accent
          ? "border-ink-900/20 bg-ink-900 text-white hover:bg-ink-800"
          : "border-black/10 bg-white/70 hover:border-black/20 hover:bg-white"
      }`}
    >
      <div className="flex items-start justify-between">
        <div
          className={`flex h-14 w-14 items-center justify-center rounded-2xl ${
            accent ? "bg-white/10 text-white" : "bg-ink-900/6 text-ink-700"
          }`}
        >
          <Icon className="h-9 w-9" />
        </div>
        <ArrowRight
          className={`size-4 transition group-hover:translate-x-0.5 ${
            accent ? "text-white/60" : "text-ink-400 group-hover:text-ink-700"
          }`}
        />
      </div>

      <div className="flex-1">
        <div className="flex items-baseline gap-2">
          <h3
            className={`font-semibold ${
              accent ? "text-white" : "text-ink-900"
            }`}
          >
            {label}
          </h3>
          {typeof count === "number" && (
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                accent
                  ? "bg-white/15 text-white/80"
                  : "bg-ink-100 text-ink-600"
              }`}
            >
              {count}
            </span>
          )}
        </div>
        <p
          className={`mt-1 text-sm leading-6 ${
            accent ? "text-white/70" : "text-ink-600"
          }`}
        >
          {description}
        </p>
      </div>

      {members && members.length > 0 && (
        <div className="flex items-center gap-2 pt-1">
          <div className="flex -space-x-2">
            {members.slice(0, 3).map((m, i) => (
              <span
                key={i}
                className={`flex h-6 w-6 items-center justify-center rounded-full border-2 text-[10px] font-bold ${
                  accent
                    ? "border-ink-800 bg-white/15 text-white"
                    : "border-white bg-ink-100 text-ink-700"
                }`}
                title={m.name}
              >
                {m.initial}
              </span>
            ))}
          </div>
          {members.length > 3 && (
            <span
              className={`text-[10px] ${
                accent ? "text-white/50" : "text-ink-400"
              }`}
            >
              +{members.length - 3}
            </span>
          )}
        </div>
      )}
    </Link>
  );
}
