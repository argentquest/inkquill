"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save, Trash2, PlusCircle, Film, FileText } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ErrorState } from "@/components/ui/error-state";
import {
  fetchAct,
  updateAct,
  deleteAct,
  fetchScenesForAct,
  createSceneForAct,
  deleteScene,
  type SceneCreatePayload,
} from "@/lib/api";

function SceneCard({ scene, actId }: { scene: { id: number; title: string; summary?: string | null; scene_number: number }; actId: number }) {
  const queryClient = useQueryClient();
  const deleteMutation = useMutation({
    mutationFn: () => deleteScene(scene.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenes", actId] });
    },
  });

  return (
    <article className="rounded-[20px] border border-black/10 bg-white/80 p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <Link href={`/storytelling/scenes/${scene.id}`}>
            <h3 className="text-sm font-semibold text-ink-900 hover:underline">
              Scene {scene.scene_number}: {scene.title}
            </h3>
          </Link>
          {scene.summary ? (
            <p className="mt-1 line-clamp-2 text-xs leading-5 text-ink-500">{scene.summary}</p>
          ) : null}
        </div>
      </div>
      <div className="mt-3 flex items-center gap-2">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/scenes/${scene.id}`}>
            <FileText className="mr-1 size-3.5" />
            Edit
          </Link>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="text-red-600 hover:text-red-700"
          onClick={() => {
            if (confirm(`Delete scene "${scene.title}"? This cannot be undone.`)) {
              deleteMutation.mutate();
            }
          }}
          disabled={deleteMutation.isPending}
        >
          <Trash2 className="mr-1 size-3.5" />
          Delete
        </Button>
      </div>
    </article>
  );
}

export default function ActEditorPage() {
  const params = useParams<{ actId: string }>();
  const actId = Number(params.actId);
  const router = useRouter();
  const queryClient = useQueryClient();

  const {
    data: act,
    isLoading: actLoading,
    isError: actError,
    error: actErr,
    refetch: refetchAct,
  } = useQuery({
    queryKey: ["act", actId],
    queryFn: () => fetchAct(actId),
    enabled: !isNaN(actId),
  });

  const {
    data: scenes,
    isLoading: scenesLoading,
    isError: scenesError,
    error: scenesErr,
    refetch: refetchScenes,
  } = useQuery({
    queryKey: ["scenes", actId],
    queryFn: () => fetchScenesForAct(actId),
    enabled: !isNaN(actId),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: { title: string; description?: string; act_summary?: string; writer_notes?: string }) =>
      updateAct(actId, payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["act", actId], data);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteAct(actId),
    onSuccess: () => {
      if (act) {
        router.push(`/storytelling/stories/${act.story_id}`);
      }
    },
  });

  const createSceneMutation = useMutation({
    mutationFn: (payload: SceneCreatePayload) => createSceneForAct(actId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scenes", actId] });
    },
  });

  function handleActSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    updateMutation.mutate({
      title: String(fd.get("title")),
      description: String(fd.get("description") || ""),
      act_summary: String(fd.get("act_summary") || ""),
      writer_notes: String(fd.get("writer_notes") || ""),
    });
  }

  function handleNewScene() {
    const title = prompt("Scene title?");
    if (!title) return;
    const nextNum = (scenes?.length ?? 0) + 1;
    createSceneMutation.mutate({ title, scene_number: nextNum });
  }

  if (actLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (actError || !act) {
    return (
      <ErrorState
        detail={actErr instanceof Error ? actErr.message : "Try refreshing the page."}
        onRetry={() => void refetchAct()}
        retryLabel="Reload act"
        title="Act could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/stories/${act.story_id}`}>
            <ArrowLeft className="mr-1 size-4" />
            Story
          </Link>
        </Button>
      </div>

      <PageHeader
        description={`Act ${act.act_number}`}
        eyebrow="Act Editor"
        title={act.title}
        action={
          <Button
            variant="destructive"
            size="sm"
            className="gap-2"
            onClick={() => {
              if (confirm(`Delete act "${act.title}"? This cannot be undone.`)) {
                deleteMutation.mutate();
              }
            }}
            disabled={deleteMutation.isPending}
          >
            <Trash2 className="size-4" />
            Delete act
          </Button>
        }
      />

      <form onSubmit={handleActSubmit} className="mx-auto max-w-2xl space-y-6">
        {(updateMutation.isError || deleteMutation.isError) && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {(updateMutation.error ?? deleteMutation.error) instanceof Error
              ? ((updateMutation.error ?? deleteMutation.error) as Error).message
              : "An error occurred."}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="title">Title *</Label>
          <Input id="title" name="title" required defaultValue={act.title} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description / Content</Label>
          <Textarea id="description" name="description" rows={6} defaultValue={act.description ?? ""} placeholder="Act description or compiled scene content..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="act_summary">Act Summary</Label>
          <Textarea id="act_summary" name="act_summary" rows={3} defaultValue={act.act_summary ?? ""} placeholder="Writer's summary of this act..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="writer_notes">Writer Notes</Label>
          <Textarea id="writer_notes" name="writer_notes" rows={3} defaultValue={act.writer_notes ?? ""} placeholder="Private notes..." />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/stories/${act.story_id}`}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={updateMutation.isPending} className="gap-2">
            {updateMutation.isPending && <Loader2 className="size-4 animate-spin" />}
            <Save className="size-4" />
            Save act
          </Button>
        </div>
      </form>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink-900">Scenes</h2>
          <Button className="gap-2" size="sm" onClick={handleNewScene} disabled={createSceneMutation.isPending}>
            <PlusCircle className="size-4" />
            New scene
          </Button>
        </div>

        {scenesLoading ? (
          <div className="flex h-32 items-center justify-center">
            <Loader2 className="size-6 animate-spin text-ink-500" />
          </div>
        ) : scenesError ? (
          <ErrorState
            detail={scenesErr instanceof Error ? scenesErr.message : "Try refreshing."}
            onRetry={() => void refetchScenes()}
            retryLabel="Reload scenes"
            title="Scenes could not be loaded."
          />
        ) : !scenes?.length ? (
          <div className="rounded-[20px] border-2 border-dashed border-black/10 bg-white/50 p-12 text-center">
            <Film className="mx-auto size-8 text-ink-400" />
            <p className="mt-3 text-sm text-ink-500">No scenes yet. Add your first scene to start building this act.</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {scenes.map((s) => (
              <SceneCard key={s.id} scene={s} actId={actId} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
