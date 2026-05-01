"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2, PlusCircle } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { createStory } from "@/lib/api";

export default function NewBasicStoryPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [shortDescription, setShortDescription] = useState("");
  const [error, setError] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      createStory({
        title: title.trim(),
        short_description: shortDescription.trim() || null,
        story_type: "basic",
      }),
    onSuccess: (data) => {
      router.push(`/storytelling/basic-stories/${data.id}`);
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
    createMutation.mutate();
  };

  return (
    <div className="space-y-8">
      <PageHeader
        description="Start a simple story with a single act and straightforward editing."
        eyebrow="Basic Story"
        title="Create a Basic Story"
        action={
          <Link href="/storytelling/stories">
            <Button className="gap-2" variant="secondary">
              <ArrowLeft className="size-4" />
              Back
            </Button>
          </Link>
        }
      />

      <form onSubmit={handleSubmit} className="mx-auto max-w-2xl space-y-6 rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        {error ? (
          <div className="rounded-[20px] border border-[#c65353]/30 bg-ember/10 px-4 py-3 text-sm text-ember">{error}</div>
        ) : null}

        <TextField label="Title" placeholder="Enter your story title" required value={title} onChange={(e) => setTitle(e.target.value)} />

        <div>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Short description</span>
            <textarea
              className="mt-2 min-h-[100px] w-full rounded-[20px] border border-black/10 bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
              placeholder="What is this story about?"
              value={shortDescription}
              onChange={(e) => setShortDescription(e.target.value)}
            />
          </label>
        </div>

        <div className="flex items-center justify-end gap-3 pt-2">
          <Link href="/storytelling/stories">
            <Button variant="secondary" type="button">Cancel</Button>
          </Link>
          <Button type="submit" disabled={createMutation.isPending || !title.trim()}>
            {createMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : <PlusCircle className="size-4" />}
            Create basic story
          </Button>
        </div>
      </form>
    </div>
  );
}
