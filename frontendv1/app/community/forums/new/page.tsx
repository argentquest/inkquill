"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Send } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { createForumThread, fetchForumCategories } from "@/lib/api";

export default function NewThreadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const appSource = searchParams.get("app_source") ?? undefined;
  const backHref = appSource === "care-circle" ? "/care-circle-family" : "/community/forums";

  const [title, setTitle] = useState("");
  const [categoryId, setCategoryId] = useState<number | "">("");
  const [content, setContent] = useState("");

  const { data: categories = [], isLoading: catsLoading } = useQuery({
    queryKey: ["forum-categories"],
    queryFn: fetchForumCategories,
  });

  const { mutate: submit, isPending, isError, error } = useMutation({
    mutationFn: () =>
      createForumThread({
        title: title.trim(),
        category_id: Number(categoryId),
        initial_post_content: content.trim(),
        app_source: appSource,
      }),
    onSuccess: (thread) => {
      router.push(`/community/forums/${thread.id}`);
    },
  });

  const canSubmit = title.trim().length > 0 && categoryId !== "" && content.trim().length > 0;

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Link
          className="flex items-center gap-1.5 text-sm text-ink-500 hover:text-ink-900"
          href={backHref}
        >
          <ArrowLeft className="size-4" />
          Back to forums
        </Link>
      </div>

      <div className="rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        <h1 className="text-2xl font-bold text-ink-900">Start a new thread</h1>
        <p className="mt-1 text-sm text-ink-500">Share a topic, ask a question, or start a discussion.</p>

        <form
          className="mt-8 space-y-6"
          onSubmit={(e) => {
            e.preventDefault();
            if (canSubmit) submit();
          }}
        >
          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="thread-title">
              Thread title
            </label>
            <input
              className="w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm text-ink-900 outline-none transition focus:border-amber-600"
              data-testid="thread-title-input"
              disabled={isPending}
              id="thread-title"
              maxLength={255}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Give your thread a clear, descriptive title"
              type="text"
              value={title}
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="thread-category">
              Category
            </label>
            {catsLoading ? (
              <div className="flex items-center gap-2 text-sm text-ink-500">
                <Loader2 className="size-4 animate-spin" /> Loading categories…
              </div>
            ) : (
              <select
                className="w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm text-ink-900 outline-none transition focus:border-amber-600"
                data-testid="thread-category-select"
                disabled={isPending}
                id="thread-category"
                onChange={(e) => setCategoryId(e.target.value === "" ? "" : Number(e.target.value))}
                value={categoryId}
              >
                <option value="">Select a category…</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="thread-content">
              Opening post
            </label>
            <textarea
              className="w-full min-h-40 rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm leading-7 text-ink-900 outline-none transition focus:border-amber-600 disabled:opacity-50"
              data-testid="thread-content-input"
              disabled={isPending}
              id="thread-content"
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your opening post…"
              value={content}
            />
          </div>

          {isError ? (
            <p className="text-sm text-red-600" data-testid="thread-create-error">
              {error instanceof Error ? error.message : "Failed to create thread. Please try again."}
            </p>
          ) : null}

          <div className="flex items-center justify-between gap-4">
            <Link className="text-sm text-ink-500 hover:text-ink-900" href={backHref}>
              Cancel
            </Link>
            <Button className="gap-2" disabled={isPending || !canSubmit} type="submit">
              {isPending ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
              {isPending ? "Creating…" : "Start thread"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
