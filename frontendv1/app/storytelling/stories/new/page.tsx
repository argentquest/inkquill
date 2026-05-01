"use client";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Sparkles, Type } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { createStory, fetchUserWorlds, type StoryCreatePayload } from "@/lib/api";

export default function NewStoryPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [storyGenre, setStoryGenre] = useState("");
  const [storyTone, setStoryTone] = useState("");
  const [primaryConflictType, setPrimaryConflictType] = useState("");
  const [storyType, setStoryType] = useState<"advanced" | "basic">("advanced");
  const [worldId, setWorldId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const { data: worlds } = useQuery({
    queryKey: ["storytelling-worlds"],
    queryFn: fetchUserWorlds,
  });

  const createMutation = useMutation({
    mutationFn: (payload: StoryCreatePayload) => createStory(payload),
    onSuccess: (data) => {
      if (storyType === "basic") {
        router.push(`/storytelling/basic-stories/${data.id}`);
      } else {
        router.push(`/storytelling/stories/${data.id}`);
      }
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
    const payload: StoryCreatePayload = {
      title: title.trim(),
      short_description: shortDescription.trim() || null,
      story_genre: storyGenre.trim() || null,
      story_tone: storyTone.trim() || null,
      primary_conflict_type: primaryConflictType.trim() || null,
      story_type: storyType,
      world_id: worldId,
    };
    createMutation.mutate(payload);
  };

  return (
    <div className="space-y-8">
      <PageHeader
        description="Start a new story by giving it a title, choosing a world, and setting the tone."
        eyebrow="New Story"
        title="Create a Story"
        action={
          <Link href="/storytelling/stories">
            <Button className="gap-2" variant="secondary">
              <ArrowLeft className="size-4" />
              Back to stories
            </Button>
          </Link>
        }
      />

      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-6 rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        {error ? (
          <div className="rounded-[20px] border border-[#c65353]/30 bg-ember/10 px-4 py-3 text-sm text-ember">
            {error}
          </div>
        ) : null}

        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => setStoryType("advanced")}
            className={`flex-1 rounded-[20px] border p-4 text-left transition ${
              storyType === "advanced" ? "border-forest bg-forest/10" : "border-black/10 bg-white/60"
            }`}
          >
            <Sparkles className="size-5 text-forest" />
            <p className="mt-2 text-sm font-semibold text-ink-900">Advanced</p>
            <p className="mt-1 text-xs text-ink-600">Full world-building with acts, scenes, and character associations.</p>
          </button>
          <button
            type="button"
            onClick={() => setStoryType("basic")}
            className={`flex-1 rounded-[20px] border p-4 text-left transition ${
              storyType === "basic" ? "border-forest bg-forest/10" : "border-black/10 bg-white/60"
            }`}
          >
            <Type className="size-5 text-ink-600" />
            <p className="mt-2 text-sm font-semibold text-ink-900">Basic</p>
            <p className="mt-1 text-xs text-ink-600">Simplified story with a single act and straightforward editor.</p>
          </button>
        </div>

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
              <option value="">{storyType === "advanced" ? "Create generic world automatically" : "None (optional)"}</option>
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
          <Link href="/storytelling/stories">
            <Button variant="secondary" type="button">
              Cancel
            </Button>
          </Link>
          <Button type="submit" disabled={createMutation.isPending || !title.trim()}>
            {createMutation.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              "Create story"
            )}
          </Button>
        </div>
      </form>
    </div>
  );
}
