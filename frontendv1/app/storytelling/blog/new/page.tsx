"use client";

import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { createBlogPost } from "@/lib/api";

export default function NewBlogPostPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [excerpt, setExcerpt] = useState("");

  const { mutate: save, isPending, isError, error } = useMutation({
    mutationFn: (asDraft: boolean) =>
      createBlogPost({ title: title.trim(), content: content.trim(), excerpt: excerpt.trim() || undefined, status: asDraft ? "draft" : "published" }),
    onSuccess: () => router.push("/storytelling/blog"),
  });

  const canSubmit = title.trim().length > 0 && content.trim().length > 0;

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Link className="flex items-center gap-1.5 text-sm text-ink-500 hover:text-ink-900" href="/storytelling/blog">
          <ArrowLeft className="size-4" />
          Back to blog
        </Link>
      </div>

      <div className="rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        <h1 className="text-2xl font-bold text-ink-900">New post</h1>

        <form className="mt-8 space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="post-title">Title</label>
            <input
              className="w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm text-ink-900 outline-none transition focus:border-amber-600"
              data-testid="post-title-input"
              disabled={isPending}
              id="post-title"
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Post title"
              type="text"
              value={title}
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="post-excerpt">Excerpt (optional)</label>
            <input
              className="w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm text-ink-900 outline-none transition focus:border-amber-600"
              data-testid="post-excerpt-input"
              disabled={isPending}
              id="post-excerpt"
              onChange={(e) => setExcerpt(e.target.value)}
              placeholder="Short summary shown in listings"
              type="text"
              value={excerpt}
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="post-content">Content</label>
            <textarea
              className="w-full min-h-64 rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm leading-7 text-ink-900 outline-none transition focus:border-amber-600 disabled:opacity-50"
              data-testid="post-content-input"
              disabled={isPending}
              id="post-content"
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your post…"
              value={content}
            />
          </div>

          {isError ? (
            <p className="text-sm text-red-600" data-testid="post-save-error">
              {error instanceof Error ? error.message : "Failed to save post."}
            </p>
          ) : null}

          <div className="flex items-center justify-between gap-4">
            <Link className="text-sm text-ink-500 hover:text-ink-900" href="/storytelling/blog">Cancel</Link>
            <div className="flex items-center gap-3">
              <Button
                disabled={isPending || !canSubmit}
                onClick={() => save(true)}
                type="button"
                variant="secondary"
              >
                {isPending ? <Loader2 className="size-4 animate-spin mr-2" /> : <Save className="size-4 mr-2" />}
                Save draft
              </Button>
              <Button
                disabled={isPending || !canSubmit}
                onClick={() => save(false)}
                type="button"
              >
                {isPending ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
                Publish
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
