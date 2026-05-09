"use client";

import Link from "next/link";

export function SectionHead({
  title,
  label,
  actionHref,
  actionLabel,
}: {
  title: string;
  label?: string;
  actionHref?: string;
  actionLabel?: string;
}) {
  return (
    <div className="space-y-3">
      <div className="flex items-baseline justify-between">
        <div className="flex items-baseline gap-2.5">
          <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-600">
            {title}
          </h2>
          {label && <span className="text-xs text-ink-400">{label}</span>}
        </div>
        {actionHref && actionLabel && (
          <Link
            href={actionHref}
            className="text-xs text-ember hover:underline"
          >
            {actionLabel} →
          </Link>
        )}
      </div>
      {/* Heavy bottom rule with ember dot */}
      <div className="flex items-center gap-2">
        <div className="h-px flex-1 bg-ink-900/15" />
        <span className="inline-block h-1.5 w-1.5 rounded-full bg-ember" />
        <div className="h-px flex-1 bg-ink-900/15" />
      </div>
    </div>
  );
}
