"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save, Trash2 } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ErrorState } from "@/components/ui/error-state";
import { fetchScene, updateScene, deleteScene } from "@/lib/api";

export default function SceneEditorPage() {
  const params = useParams<{ sceneId: string }>();
  const sceneId = Number(params.sceneId);
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: scene, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["scene", sceneId],
    queryFn: () => fetchScene(sceneId),
    enabled: !isNaN(sceneId),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: { title: string; content?: string; summary?: string; mood?: string; characters_present?: string; plot_points?: string }) =>
      updateScene(sceneId, payload),
    onSuccess: (data) => {
      queryClient.setQueryData(["scene", sceneId], data);
      queryClient.invalidateQueries({ queryKey: ["scenes", data.act_id] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteScene(sceneId),
    onSuccess: () => {
      if (scene) {
        router.push(`/storytelling/acts/${scene.act_id}`);
      }
    },
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    updateMutation.mutate({
      title: String(fd.get("title")),
      content: String(fd.get("content") || ""),
      summary: String(fd.get("summary") || ""),
      mood: String(fd.get("mood") || ""),
      characters_present: String(fd.get("characters_present") || ""),
      plot_points: String(fd.get("plot_points") || ""),
    });
  }

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !scene) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "Try refreshing the page."}
        onRetry={() => void refetch()}
        retryLabel="Reload scene"
        title="Scene could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/acts/${scene.act_id}`}>
            <ArrowLeft className="mr-1 size-4" />
            Act
          </Link>
        </Button>
      </div>

      <PageHeader
        description={scene.summary || "Scene editor"}
        eyebrow={`Scene ${scene.scene_number}`}
        title={scene.title}
        action={
          <Button
            variant="destructive"
            size="sm"
            className="gap-2"
            onClick={() => {
              if (confirm(`Delete scene "${scene.title}"? This cannot be undone.`)) {
                deleteMutation.mutate();
              }
            }}
            disabled={deleteMutation.isPending}
          >
            <Trash2 className="size-4" />
            Delete
          </Button>
        }
      />

      <form onSubmit={handleSubmit} className="mx-auto max-w-3xl space-y-6">
        {(updateMutation.isError || deleteMutation.isError) && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {(updateMutation.error ?? deleteMutation.error) instanceof Error
              ? ((updateMutation.error ?? deleteMutation.error) as Error).message
              : "An error occurred."}
          </div>
        )}

        <div className="space-y-2">
          <Label htmlFor="title">Title *</Label>
          <Input id="title" name="title" required defaultValue={scene.title} />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="mood">Mood</Label>
            <Input id="mood" name="mood" defaultValue={scene.mood ?? ""} placeholder="Suspenseful, lighthearted..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="characters_present">Characters Present</Label>
            <Input id="characters_present" name="characters_present" defaultValue={scene.characters_present ?? ""} placeholder="Comma-separated names..." />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="plot_points">Plot Points</Label>
          <Textarea id="plot_points" name="plot_points" rows={3} defaultValue={scene.plot_points ?? ""} placeholder="Key events in this scene..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="summary">Summary</Label>
          <Textarea id="summary" name="summary" rows={3} defaultValue={scene.summary ?? ""} placeholder="Writer's intent and summary..." />
        </div>

        <div className="space-y-2">
          <Label htmlFor="content">Content</Label>
          <Textarea id="content" name="content" rows={12} defaultValue={scene.content ?? ""} placeholder="Write the scene narrative here..." />
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button asChild variant="outline">
            <Link href={`/storytelling/acts/${scene.act_id}`}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={updateMutation.isPending} className="gap-2">
            {updateMutation.isPending && <Loader2 className="size-4 animate-spin" />}
            <Save className="size-4" />
            Save scene
          </Button>
        </div>
      </form>
    </div>
  );
}
