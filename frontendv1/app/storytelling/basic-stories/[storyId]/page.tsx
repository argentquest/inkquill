"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save, Type } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { TextField } from "@/components/ui/text-field";
import { fetchStory, fetchActsForStory, updateStory } from "@/lib/api";

export default function BasicStoryEditorPage() {
  const params = useParams();
  const router = useRouter();
  const storyId = Number(params.storyId);

  const [title, setTitle] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

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

  useEffect(() => {
    if (storyQuery.data) {
      setTitle(storyQuery.data.title);
      setShortDescription(storyQuery.data.short_description ?? "");
    }
    if (actsQuery.data && actsQuery.data.length > 0) {
      setContent(actsQuery.data[0].description ?? "");
    }
  }, [storyQuery.data, actsQuery.data]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      const storyPayload = {
        title: title.trim(),
        short_description: shortDescription.trim() || null,
      };
      await updateStory(storyId, storyPayload);
      // Update act content via the basic story API
      const actId = actsQuery.data?.[0]?.id;
      if (actId) {
        await fetch(`/api/v1/acts/${actId}`, {
          method: "PUT",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ description: content }),
        });
      }
    },
    onSuccess: () => {
      router.push(`/storytelling/stories/${storyId}`);
    },
    onError: (err: Error) => setError(err.message),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!title.trim()) {
      setError("Title is required.");
      return;
    }
    saveMutation.mutate();
  };

  if (storyQuery.isLoading || actsQuery.isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-8 animate-spin text-ink-500" />
      </div>
    );
  }

  if (storyQuery.isError || actsQuery.isError) {
    return (
      <ErrorState
        detail={(storyQuery.error ?? actsQuery.error) instanceof Error ? ((storyQuery.error ?? actsQuery.error) as Error).message : "Try refreshing the page."}
        onRetry={() => {
          void storyQuery.refetch();
          void actsQuery.refetch();
        }}
        retryLabel="Reload"
        title="Story could not be loaded."
      />
    );
  }

  const story = storyQuery.data;
  if (story && story.story_type !== "basic") {
    return (
      <div className="space-y-8">
        <PageHeader eyebrow="Story" title="Not a Basic Story" description="This story is an advanced story. Use the standard story editor." />
        <Link href={`/storytelling/stories/${storyId}`}>
          <Button variant="secondary">Go to story</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        description="Keep your writing simple. Edit the title, description, and story content."
        eyebrow="Basic Story"
        title={title}
        action={
          <div className="flex flex-wrap gap-2">
            <Link href={`/storytelling/stories/${storyId}`}>
              <Button className="gap-2" variant="secondary">
                <ArrowLeft className="size-4" />
                Back
              </Button>
            </Link>
            <Button className="gap-2" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />}
              Save
            </Button>
          </div>
        }
      />

      <form onSubmit={handleSubmit} className="mx-auto max-w-3xl space-y-6 rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        {error ? (
          <div className="rounded-[20px] border border-[#c65353]/30 bg-ember/10 px-4 py-3 text-sm text-ember">{error}</div>
        ) : null}

        <TextField label="Title" placeholder="Story title" required value={title} onChange={(e) => setTitle(e.target.value)} />

        <div>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Short description</span>
            <textarea
              className="mt-2 min-h-[80px] w-full rounded-[20px] border border-black/10 bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
              placeholder="A brief summary of your story"
              value={shortDescription}
              onChange={(e) => setShortDescription(e.target.value)}
            />
          </label>
        </div>

        <div>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Story content</span>
            <textarea
              className="mt-2 min-h-[400px] w-full rounded-[20px] border border-black/10 bg-white/85 px-4 py-3 text-sm leading-7 text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
              placeholder="Start writing your story..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </label>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Link href={`/storytelling/stories/${storyId}`}>
            <Button variant="secondary" type="button">
              Cancel
            </Button>
          </Link>
          <Button type="submit" disabled={saveMutation.isPending || !title.trim()}>
            {saveMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <Save className="size-4" />}
            Save changes
          </Button>
        </div>
      </form>
    </div>
  );
}
