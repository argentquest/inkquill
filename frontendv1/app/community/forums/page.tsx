"use client";

import { useQuery } from "@tanstack/react-query";
import { Loader2, MessageSquare, PenLine } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { fetchForumCategories, fetchForumThreads, type ForumCategory, type ForumThreadSummary } from "@/lib/api";

function CategoryCard({ category }: { category: ForumCategory }) {
  return (
    <div className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
      <div className="flex items-start gap-4">
        {category.icon ? (
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-paper text-2xl shadow-sm">
            {category.icon}
          </span>
        ) : (
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400 shadow-sm">
            <MessageSquare className="size-6" />
          </div>
        )}
        <div className="min-w-0 flex-1">
          <h2 className="text-base font-semibold text-ink-900">{category.name}</h2>
          {category.description ? (
            <p className="mt-1 text-sm text-ink-600">{category.description}</p>
          ) : null}
          <p className="mt-2 text-xs text-ink-500">
            {category.thread_count} {category.thread_count === 1 ? "thread" : "threads"}
          </p>
        </div>
      </div>
    </div>
  );
}

function ThreadRow({ thread }: { thread: ForumThreadSummary }) {
  return (
    <Link href={`/community/forums/${thread.id}`}>
      <article className="flex items-start gap-4 rounded-2xl border border-black/10 bg-white/80 p-4 shadow-sm transition-shadow hover:shadow-md">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400">
          <MessageSquare className="size-5" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold text-ink-900">{thread.title}</h3>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-ink-500">
            <span>by {thread.username}</span>
            {thread.category_name ? (
              <span className="rounded-full bg-black/[0.05] px-2 py-0.5 font-medium text-ink-700">
                {thread.category_name}
              </span>
            ) : null}
            <span>{thread.post_count} {thread.post_count === 1 ? "reply" : "replies"}</span>
            <span>{thread.view_count.toLocaleString()} views</span>
            {thread.is_pinned ? <span className="font-medium text-ink-700">Pinned</span> : null}
          </div>
        </div>
      </article>
    </Link>
  );
}

export default function ForumCategoriesPage() {
  const { data: categories = [], isLoading: catLoading, isError: catError, error: catErr, refetch: refetchCat } = useQuery({
    queryKey: ["forum-categories"],
    queryFn: fetchForumCategories,
  });

  const { data: threads = [], isLoading: threadLoading } = useQuery({
    queryKey: ["forum-threads-recent"],
    queryFn: () => fetchForumThreads(),
  });

  const isLoading = catLoading || threadLoading;

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <PageHeader
          description="Discussion categories and recent threads from the Ink and Quill writing community."
          eyebrow="Community Forums"
          title="Forums"
        />
        <Link
          className="mt-1 flex shrink-0 items-center gap-2 rounded-full bg-ink-900 px-4 py-2.5 text-sm font-medium text-paper shadow-sm transition hover:bg-ink-700"
          data-testid="new-thread-link"
          href="/community/forums/new"
        >
          <PenLine className="size-4" />
          New thread
        </Link>
      </div>

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : catError ? (
        <ErrorState
          detail={catErr instanceof Error ? catErr.message : "Try refreshing the page."}
          onRetry={() => void refetchCat()}
          retryLabel="Reload forums"
          title="Forums could not be loaded."
        />
      ) : (
        <div className="space-y-10">
          {categories.length > 0 ? (
            <section className="space-y-4" data-testid="forum-categories">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Categories</h2>
              <div className="grid gap-4 md:grid-cols-2">
                {categories.map((cat) => (
                  <CategoryCard key={cat.id} category={cat} />
                ))}
              </div>
            </section>
          ) : (
            <section
              className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
              data-testid="forum-empty-state"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
                <MessageSquare className="size-8" />
              </div>
              <h3 className="mt-4 text-base font-bold text-ink-900">No forum categories yet</h3>
              <p className="mt-2 max-w-sm text-sm text-ink-500">
                Forum categories will appear here once they are set up.
              </p>
            </section>
          )}

          {threads.length > 0 ? (
            <section className="space-y-4" data-testid="forum-recent-threads">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Recent Threads</h2>
              <div className="space-y-3">
                {threads.slice(0, 10).map((thread) => (
                  <ThreadRow key={thread.id} thread={thread} />
                ))}
              </div>
            </section>
          ) : null}
        </div>
      )}
    </div>
  );
}
