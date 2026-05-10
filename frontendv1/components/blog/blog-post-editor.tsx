"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2, Save } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { RichTextEditor } from "@/components/ui/rich-text-editor";
import { createBlogPost, fetchBlogPostById, publishBlogPost, updateBlogPost } from "@/lib/api";

interface BlogPostEditorProps {
  basePath: string;
  appSource?: string;
  postId?: number;
}

export function BlogPostEditor({ basePath, appSource, postId }: BlogPostEditorProps) {
  const router = useRouter();
  const isNew = postId === undefined;

  const { data: post, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["blog-post-edit", postId],
    queryFn: () => fetchBlogPostById(postId!),
    enabled: !isNew && !isNaN(postId!),
  });

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [dirty, setDirty] = useState(false);

  useEffect(() => {
    if (post) {
      setTitle(post.title);
      setContent(post.content);
      setExcerpt(post.excerpt ?? "");
      setDirty(false);
    }
  }, [post]);

  const { mutate: save, isPending: isSaving, isError: saveError, error: saveErr } = useMutation({
    mutationFn: () => {
      if (isNew) {
        return createBlogPost({
          title: title.trim(),
          content: content.trim(),
          excerpt: excerpt.trim() || undefined,
          status: "published",
          app_source: appSource,
        });
      }
      return updateBlogPost(postId!, { title: title.trim(), content: content.trim(), excerpt: excerpt.trim() || undefined });
    },
    onSuccess: () => {
      setDirty(false);
      router.push(basePath);
    },
  });

  const { mutate: saveDraft, isPending: isDraftSaving } = useMutation({
    mutationFn: () =>
      createBlogPost({
        title: title.trim(),
        content: content.trim(),
        excerpt: excerpt.trim() || undefined,
        status: "draft",
        app_source: appSource,
      }),
    onSuccess: () => router.push(basePath),
  });

  const { mutate: doPublish, isPending: isPublishing } = useMutation({
    mutationFn: () => publishBlogPost(postId!),
    onSuccess: () => router.push(basePath),
  });

  const isPending = isSaving || isDraftSaving || isPublishing;
  const canSubmit = title.trim().length > 0 && content.replace(/<[^>]*>/g, "").trim().length > 0;

  if (!isNew && isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (!isNew && (isError || !post)) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "The post may have been deleted."}
        onRetry={() => void refetch()}
        retryLabel="Reload post"
        title="Post could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <Link className="flex items-center gap-1.5 text-sm text-ink-500 hover:text-ink-900" href={basePath}>
          <ArrowLeft className="size-4" />
          Back to blog
        </Link>
      </div>

      <div className="rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        <div className="flex items-center justify-between gap-4">
          <h1 className="text-2xl font-bold text-ink-900">{isNew ? "New post" : "Edit post"}</h1>
          {!isNew ? (
            <div className="flex items-center gap-2 text-sm">
              <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${post!.status === "published" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
                {post!.status}
              </span>
              {dirty ? <span className="text-xs text-ink-500">Unsaved changes</span> : null}
            </div>
          ) : null}
        </div>

        <form className="mt-8 space-y-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="post-title">Title</label>
            <input
              className="w-full rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm text-ink-900 outline-none transition focus:border-amber-600"
              data-testid="post-title-input"
              disabled={isPending}
              id="post-title"
              onChange={(e) => { setTitle(e.target.value); setDirty(true); }}
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
              onChange={(e) => { setExcerpt(e.target.value); setDirty(true); }}
              placeholder="Short summary shown in listings"
              type="text"
              value={excerpt}
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-ink-800" htmlFor="post-content">Content</label>
            <RichTextEditor
              disabled={isPending}
              minHeight="16rem"
              onChange={(html) => { setContent(html); setDirty(true); }}
              placeholder="Write your post…"
              value={content}
              variant="full"
            />
          </div>

          {saveError ? (
            <p className="text-sm text-red-600" data-testid="post-save-error">
              {saveErr instanceof Error ? saveErr.message : "Failed to save post."}
            </p>
          ) : null}

          <div className="flex items-center justify-between gap-4">
            <Link className="text-sm text-ink-500 hover:text-ink-900" href={basePath}>Cancel</Link>
            <div className="flex items-center gap-3">
              {isNew ? (
                <>
                  <Button
                    disabled={isPending || !canSubmit}
                    onClick={() => saveDraft()}
                    type="button"
                    variant="secondary"
                  >
                    {isDraftSaving ? <Loader2 className="size-4 animate-spin mr-2" /> : <Save className="size-4 mr-2" />}
                    Save draft
                  </Button>
                  <Button
                    disabled={isPending || !canSubmit}
                    onClick={() => save()}
                    type="button"
                  >
                    {isSaving ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
                    Publish
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    disabled={isPending || !canSubmit || !dirty}
                    onClick={() => save()}
                    type="button"
                    variant="secondary"
                  >
                    {isSaving ? <Loader2 className="size-4 animate-spin mr-2" /> : <Save className="size-4 mr-2" />}
                    Save
                  </Button>
                  {post!.status !== "published" ? (
                    <Button
                      disabled={isPending || !canSubmit}
                      onClick={() => doPublish()}
                      type="button"
                    >
                      {isPublishing ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
                      Publish
                    </Button>
                  ) : null}
                </>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
