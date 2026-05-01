"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Loader2, PlusCircle, Trash2, ExternalLink, Sparkles } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { ConfirmDialog } from "@/components/ui/dialog";
import { fetchUserStories, deleteStory, type StoryEntry } from "@/lib/api";

function StoryCard({ story, onDelete }: { story: StoryEntry; onDelete: (id: number) => void }) {
  return (
    <article className="group rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel transition hover:shadow-lg">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <Link href={`/storytelling/stories/${story.id}`} className="block">
            <h2 className="truncate text-base font-semibold text-ink-900 group-hover:text-forest transition">
              {story.title}
            </h2>
          </Link>
          {story.short_description ? (
            <p className="mt-1 line-clamp-2 text-sm leading-6 text-ink-600">{story.short_description}</p>
          ) : null}
          <div className="mt-3 flex flex-wrap gap-2">
            {story.story_genre ? (
              <span className="rounded-full bg-black/[0.05] px-2.5 py-1 text-xs font-medium text-ink-700">
                {story.story_genre}
              </span>
            ) : null}
            <span className="rounded-full bg-black/[0.05] px-2.5 py-1 text-xs font-medium text-ink-500 capitalize">
              {story.story_type}
            </span>
          </div>
          <div className="mt-4 flex items-center gap-3">
            <Link
              href={`/storytelling/stories/${story.id}`}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-forest hover:underline"
            >
              Open story <ExternalLink className="size-3" />
            </Link>
            <Link
              href={`/storytelling/stories/${story.id}/edit`}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-ink-600 hover:underline"
            >
              Edit
            </Link>
            <button
              onClick={() => onDelete(story.id)}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-ember hover:underline"
              data-testid={`story-delete-${story.id}`}
            >
              <Trash2 className="size-3" /> Delete
            </button>
          </div>
        </div>
        <div className="flex shrink-0 items-center justify-center rounded-full bg-paper p-3 text-ink-400 group-hover:text-forest transition">
          <BookOpen className="size-5" />
        </div>
      </div>
    </article>
  );
}

export default function StoriesPage() {
  const queryClient = useQueryClient();
  const { data: stories, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["storytelling-stories"],
    queryFn: fetchUserStories,
  });

  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);

  const deleteMutation = useMutation({
    mutationFn: deleteStory,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["storytelling-stories"] });
      setDeleteTarget(null);
    },
  });

  return (
    <div className="space-y-8">
      <PageHeader
        description="Your story drafts, works in progress, and published pieces live here. Each story is linked to a world."
        eyebrow="Stories"
        title="Your Stories"
        action={
          <div className="flex flex-wrap gap-3">
            <Link href="/storytelling/stories/wizard">
              <Button className="gap-2">
                <Sparkles className="size-4" />
                Wizard
              </Button>
            </Link>
            <Link href="/storytelling/stories/new">
              <Button className="gap-2">
                <PlusCircle className="size-4" />
                Create story
              </Button>
            </Link>
          </div>
        }
      />

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try refreshing the page."}
          onRetry={() => void refetch()}
          retryLabel="Reload stories"
          title="Stories could not be loaded."
        />
      ) : !stories?.length ? (
        <section
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
          data-testid="stories-empty-state"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <BookOpen className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No stories yet</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">
            Create your first story to begin building acts, scenes, and narrative arcs within a world.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/storytelling/stories/wizard">
              <Button className="gap-2">
                <Sparkles className="size-4" />
                Use Wizard
              </Button>
            </Link>
            <Link href="/storytelling/stories/new">
              <Button className="gap-2">
                <PlusCircle className="size-4" />
                Create a story
              </Button>
            </Link>
          </div>
        </section>
      ) : (
        <section className="space-y-4" data-testid="stories-list">
          <p className="text-sm text-ink-600">
            {stories.length} {stories.length === 1 ? "story" : "stories"}
          </p>
          <div className="grid gap-4 md:grid-cols-2">
            {stories.map((story) => (
              <StoryCard key={story.id} story={story} onDelete={(id) => setDeleteTarget(id)} />
            ))}
          </div>
        </section>
      )}

      <ConfirmDialog
        open={deleteTarget !== null}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
        }}
        title="Delete Story"
        description="This will permanently delete the story and all associated acts, scenes, and content. This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="destructive"
        onConfirm={() => {
          if (deleteTarget !== null) {
            deleteMutation.mutate(deleteTarget);
          }
        }}
      />
    </div>
  );
}
