"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  BookOpen,
  Edit3,
  Globe,
  Loader2,
  PlusCircle,
  Rocket,
  Trash2,
  Zap,
  MessageSquare,
} from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { ConfirmDialog } from "@/components/ui/dialog";
import {
  fetchStory,
  fetchActsForStory,
  deleteStory,
  publishStory,
  upgradeStory,
  type StoryDetail,
  type ActEntry,
} from "@/lib/api";

function ActCard({ act }: { act: ActEntry }) {
  return (
    <div className="rounded-[20px] border border-black/10 bg-white/70 p-5 shadow-sm transition hover:bg-white/90">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-forest">
            Act {act.act_number}
          </p>
          <h3 className="mt-1 text-sm font-semibold text-ink-900">{act.title}</h3>
          {act.description ? (
            <p className="mt-2 line-clamp-3 text-sm leading-6 text-ink-600">{act.description}</p>
          ) : null}
          {act.act_summary ? (
            <p className="mt-2 text-xs italic text-ink-500">{act.act_summary}</p>
          ) : null}
        </div>
        <div className="rounded-full bg-paper p-2.5 text-ink-400">
          <BookOpen className="size-4" />
        </div>
      </div>
    </div>
  );
}

export default function StoryDetailPage() {
  const params = useParams();
  const router = useRouter();
  const storyId = Number(params.storyId);
  const queryClient = useQueryClient();

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showPublishConfirm, setShowPublishConfirm] = useState(false);
  const [showUpgradeConfirm, setShowUpgradeConfirm] = useState(false);
  const [actionError, setActionError] = useState("");

  const storyQuery = useQuery({
    queryKey: ["story", storyId],
    queryFn: () => fetchStory(storyId),
    enabled: !isNaN(storyId),
  });

  const actsQuery = useQuery({
    queryKey: ["story-acts", storyId],
    queryFn: () => fetchActsForStory(storyId),
    enabled: !isNaN(storyId),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteStory(storyId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["storytelling-stories"] });
      router.push("/storytelling/stories");
    },
    onError: (err: Error) => setActionError(err.message),
  });

  const publishMutation = useMutation({
    mutationFn: () => publishStory(storyId, { visibility: "public" }),
    onSuccess: () => {
      setShowPublishConfirm(false);
      void queryClient.invalidateQueries({ queryKey: ["story", storyId] });
    },
    onError: (err: Error) => setActionError(err.message),
  });

  const upgradeMutation = useMutation({
    mutationFn: () => upgradeStory(storyId, {}),
    onSuccess: () => {
      setShowUpgradeConfirm(false);
      void queryClient.invalidateQueries({ queryKey: ["story", storyId] });
    },
    onError: (err: Error) => setActionError(err.message),
  });

  const isLoading = storyQuery.isLoading || actsQuery.isLoading;
  const isError = storyQuery.isError || actsQuery.isError;
  const error = storyQuery.error || actsQuery.error;

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-8 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing the page."}
        onRetry={() => {
          void storyQuery.refetch();
          void actsQuery.refetch();
        }}
        retryLabel="Reload story"
        title="Story could not be loaded."
      />
    );
  }

  const story = storyQuery.data as StoryDetail;
  const acts = (actsQuery.data ?? []) as ActEntry[];

  return (
    <div className="space-y-8">
      <PageHeader
        description={story.short_description || "Manage your story, acts, and scenes."}
        eyebrow="Story"
        title={story.title}
        action={
          <div className="flex flex-wrap gap-2">
            <Link href="/storytelling/stories">
              <Button className="gap-2" variant="secondary">
                <ArrowLeft className="size-4" />
                Back
              </Button>
            </Link>
            <Link href={`/storytelling/stories/${story.id}/edit`}>
              <Button className="gap-2" variant="secondary">
                <Edit3 className="size-4" />
                Edit
              </Button>
            </Link>
            <Link href={`/storytelling/stories/${story.id}/chat`}>
              <Button className="gap-2" variant="secondary">
                <MessageSquare className="size-4" />
                Chat
              </Button>
            </Link>
            {story.story_type === "basic" && (
              <Button className="gap-2" onClick={() => setShowUpgradeConfirm(true)} variant="secondary">
                <Zap className="size-4" />
                Upgrade
              </Button>
            )}
            <Button className="gap-2" onClick={() => setShowPublishConfirm(true)}>
              <Rocket className="size-4" />
              Publish
            </Button>
            <Button className="gap-2" variant="ghost" onClick={() => setShowDeleteConfirm(true)}>
              <Trash2 className="size-4" />
            </Button>
          </div>
        }
      />

      {actionError ? (
        <div className="rounded-[20px] border border-[#c65353]/30 bg-ember/10 px-4 py-3 text-sm text-ember">
          {actionError}
        </div>
      ) : null}

      {/* Story metadata */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-[20px] border border-black/10 bg-white/70 p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-500">Type</p>
          <p className="mt-1 text-sm font-medium capitalize text-ink-900">{story.story_type}</p>
        </div>
        <div className="rounded-[20px] border border-black/10 bg-white/70 p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-500">Genre</p>
          <p className="mt-1 text-sm font-medium text-ink-900">{story.story_genre || "—"}</p>
        </div>
        <div className="rounded-[20px] border border-black/10 bg-white/70 p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-500">Tone</p>
          <p className="mt-1 text-sm font-medium text-ink-900">{story.story_tone || "—"}</p>
        </div>
        <div className="rounded-[20px] border border-black/10 bg-white/70 p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ink-500">World ID</p>
          <p className="mt-1 text-sm font-medium text-ink-900">{story.world_id}</p>
        </div>
      </section>

      {story.ai_summary ? (
        <section className="rounded-[20px] border border-black/10 bg-white/70 p-5 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-forest">AI Summary</p>
          <p className="mt-2 text-sm leading-6 text-ink-700">{story.ai_summary}</p>
        </section>
      ) : null}

      {/* Acts */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink-900">Acts</h2>
          <Button className="gap-2" variant="secondary" disabled>
            <PlusCircle className="size-4" />
            Add act
          </Button>
        </div>

        {acts.length === 0 ? (
          <div className="rounded-[20px] border border-dashed border-black/10 bg-white/50 p-8 text-center">
            <Globe className="mx-auto size-6 text-ink-400" />
            <p className="mt-2 text-sm text-ink-600">No acts yet.</p>
            <p className="text-xs text-ink-500">Acts will appear here once created.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {acts.map((act) => (
              <ActCard key={act.id} act={act} />
            ))}
          </div>
        )}
      </section>

      <ConfirmDialog
        open={showDeleteConfirm}
        onOpenChange={setShowDeleteConfirm}
        title="Delete Story"
        description="Permanently delete this story and all its acts and scenes? This cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        variant="destructive"
        onConfirm={() => deleteMutation.mutate()}
      />

      <ConfirmDialog
        open={showPublishConfirm}
        onOpenChange={setShowPublishConfirm}
        title="Publish Story"
        description="Publish this story as a public HTML page? You can unpublish later from the published stories section."
        confirmLabel="Publish"
        cancelLabel="Cancel"
        variant="primary"
        onConfirm={() => publishMutation.mutate()}
      />

      <ConfirmDialog
        open={showUpgradeConfirm}
        onOpenChange={setShowUpgradeConfirm}
        title="Upgrade to Advanced"
        description="Convert this Basic Story to an Advanced Story with full world-building support. This cannot be reversed."
        confirmLabel="Upgrade"
        cancelLabel="Cancel"
        variant="primary"
        onConfirm={() => upgradeMutation.mutate()}
      />
    </div>
  );
}
