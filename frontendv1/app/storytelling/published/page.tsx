"use client";

import { useQuery } from "@tanstack/react-query";
import { BookOpen, ExternalLink, Loader2, Star } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { fetchPublishedStories, fetchSession, type PublishedStoryEntry } from "@/lib/api";

function PublishedStoryCard({ story }: { story: PublishedStoryEntry }) {
  return (
    <article className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h2 className="truncate text-base font-semibold text-ink-900">{story.title}</h2>
          {story.description ? (
            <p className="mt-1 line-clamp-2 text-sm leading-6 text-ink-600">{story.description}</p>
          ) : null}
          <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-ink-500">
            {story.world_name ? (
              <span className="rounded-full bg-black/[0.05] px-2.5 py-1 font-medium text-ink-700">
                {story.world_name}
              </span>
            ) : null}
            {story.word_count ? <span>{story.word_count.toLocaleString()} words</span> : null}
            <span>{story.view_count.toLocaleString()} views</span>
            {story.average_rating ? (
              <span className="flex items-center gap-1">
                <Star className="size-3" />
                {story.average_rating.toFixed(1)}
              </span>
            ) : null}
          </div>
        </div>
        <Link
          className="flex shrink-0 items-center justify-center rounded-full bg-paper p-3 text-ink-400 hover:text-ink-700"
          href={`/public/stories/${story.id}`}
        >
          <ExternalLink className="size-5" />
        </Link>
      </div>
    </article>
  );
}

export default function MyPublishedStoriesPage() {
  const { data: session } = useQuery({
    queryKey: ["session"],
    queryFn: fetchSession,
  });

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["my-published-stories", session?.id],
    queryFn: () => fetchPublishedStories({ sort_by: "recent", per_page: 100 }),
    enabled: !!session,
  });

  const stories = (data?.stories ?? []).filter((s) => s.user_id === session?.id);

  return (
    <div className="space-y-8">
      <PageHeader
        description="Stories you have published to the public reader. Each published story is linked back to its source in your storytelling workspace."
        eyebrow="Published"
        title="Your Published Stories"
      />

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try refreshing the page."}
          onRetry={() => void refetch()}
          retryLabel="Reload published stories"
          title="Published stories could not be loaded."
        />
      ) : !stories.length ? (
        <section
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
          data-testid="my-published-empty-state"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <BookOpen className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No published stories yet</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">
            When you publish a story it will appear here with its reader stats.
          </p>
        </section>
      ) : (
        <section className="space-y-4" data-testid="my-published-list">
          <p className="text-sm text-ink-600">
            {stories.length} {stories.length === 1 ? "published story" : "published stories"}
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            {stories.map((story) => (
              <PublishedStoryCard key={story.id} story={story} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
