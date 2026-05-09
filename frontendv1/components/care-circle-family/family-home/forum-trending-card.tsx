"use client";

import Link from "next/link";
import { MessageSquare } from "lucide-react";
import type { ForumThreadSummary } from "@/lib/api";

export function ForumTrendingCard({
  thread,
}: {
  thread?: ForumThreadSummary | null;
}) {
  if (!thread) return null;

  return (
    <Link
      href={`/community/forums/${thread.id}`}
      className="group block rounded-[24px] border border-black/10 bg-white/70 p-5 shadow-panel transition hover:border-black/20 hover:bg-white"
    >
      <div className="flex items-center gap-2">
        <MessageSquare className="h-4 w-4 text-ember" />
        <span className="text-xs font-semibold uppercase tracking-wider text-ink-400">
          Trending
        </span>
      </div>
      <h3 className="mt-3 font-display text-lg font-semibold text-ink-900 group-hover:text-ember">
        {thread.title}
      </h3>
      <p className="mt-1 text-xs text-ink-500">
        {thread.category_name ?? "Forum"} · {thread.post_count} replies
      </p>
    </Link>
  );
}
