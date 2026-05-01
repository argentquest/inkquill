"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { fetchStory, updateStory, fetchUserWorlds } from "@/lib/api";

export default function EditStoryPage() {
  const params = useParams();
  const router = useRouter();
  const storyId = Number(params.storyId);

  const [title, setTitle] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [storyGenre, setStoryGenre] = useState("");
  const [storyTone, setStoryTone] = useState("");
  const [primaryConflictType, setPrimaryConflictType] = useState("");
  const [worldId, setWorldId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const { data: story, isLoading: storyLoading } = useQuery({
    queryKey: ["story", storyId],
    queryFn: () => fetchStory(storyId),
    enabled: !isNaN(storyId),
  });

  const { data: worlds } = useQuery({
    queryKey: ["storytelling-worlds"],
    queryFn: fetchUserWorlds,
  });

  useEffect(() => {
    if (story) {
      setTitle(story.title);
      setShortDescription(story.short_description ?? "");
      setStoryGenre(story.story_genre ?? "");
      setStoryTone(story.story_tone ?? "");
      setPrimaryConflictType(story.primary_conflict_type ?? "");
      setWorldId(story.world_id ?? null);
    }
  }, [story]);

  const updateMutation = useMutation({
    mutationFn: () =>
      updateStory(storyId, {
        title: title.trim(),
        short_description: shortDescription.trim() || null,
        story_genre: storyGenre.trim() || null,
        story_tone: storyTone.trim() || null,
        primary_conflict_type: primaryConflictType.trim() || null,
        world_id: worldId,
      }),
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
    updateMutation.mutate();
  };

  if (storyLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-8 animate-spin text-ink-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        description="Update your story title, genre, tone, world, and description."
        eyebrow="Edit Story"
        title={story?.title ?? "Edit Story"}
        action={
          <Link href={`/storytelling/stories/${storyId}`}>
            <Button className="gap-2" variant="secondary">
              <ArrowLeft className="size-4" />
              Back to story
            </Button>
          </Link>
        }
      />

      <form
        onSubmit={handleSubmit}
        className="mx-auto max-w-2xl space-y-6 rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel"
      >
        {error ? (
          <div className="rounded-[20px] border border-[#c65353]/30 bg-ember/10 px-4 py-3 text-sm text-ember">
            {error}
          </div>
        ) : null}

        <TextField
          label="Title"
          placeholder="Enter your story title"
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <TextField
            label="Genre"
            placeholder="e.g. Fantasy Adventure"
            value={storyGenre}
            onChange={(e) => setStoryGenre(e.target.value)}
          />
          <TextField
            label="Tone"
            placeholder="e.g. Dark, Hopeful"
            value={storyTone}
            onChange={(e) => setStoryTone(e.target.value)}
          />
        </div>

        <TextField
          label="Primary Conflict"
          placeholder="e.g. Character vs. Self"
          value={primaryConflictType}
          onChange={(e) => setPrimaryConflictType(e.target.value)}
        />

        <div>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.24em] text-ink-600">World</span>
            <select
              className="mt-2 w-full rounded-[20px] border border-black/10 bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
              value={worldId ?? ""}
              onChange={(e) => setWorldId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">None</option>
              {worlds?.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Short description</span>
            <textarea
              className="mt-2 min-h-[120px] w-full rounded-[20px] border border-black/10 bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
              placeholder="What is this story about?"
              value={shortDescription}
              onChange={(e) => setShortDescription(e.target.value)}
            />
          </label>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Link href={`/storytelling/stories/${storyId}`}>
            <Button variant="secondary" type="button">
              Cancel
            </Button>
          </Link>
          <Button type="submit" disabled={updateMutation.isPending || !title.trim()}>
            {updateMutation.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Save className="size-4" />
            )}
            Save changes
          </Button>
        </div>
      </form>
    </div>
  );
}
