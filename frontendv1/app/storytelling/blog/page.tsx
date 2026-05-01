"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileText, Loader2, Pencil, Plus, Trash2 } from "lucide-react";
import Link from "next/link";

import { useSession } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { deleteBlogPost, fetchAuthorBlogPosts, publishBlogPost, type BlogPost } from "@/lib/api";

function statusBadge(status: string) {
  if (status === "published")
    return <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">Published</span>;
  if (status === "draft")
    return <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">Draft</span>;
  return <span className="rounded-full bg-black/[0.05] px-2 py-0.5 text-xs font-medium text-ink-600">{status}</span>;
}

function PostRow({
  post,
  onDelete,
  onPublish,
}: {
  post: BlogPost;
  onDelete: (id: number) => void;
  onPublish: (id: number) => void;
}) {
  return (
    <article className="flex items-start justify-between gap-4 rounded-2xl border border-black/10 bg-white/80 p-5 shadow-sm" data-testid="blog-post-row">
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          {statusBadge(post.status)}
          <span className="text-xs text-ink-500">
            {new Date(post.updated_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
          </span>
        </div>
        <h3 className="mt-2 text-sm font-semibold text-ink-900">{post.title}</h3>
        {post.excerpt ? (
          <p className="mt-1 line-clamp-2 text-sm text-ink-600">{post.excerpt}</p>
        ) : null}
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {post.status === "draft" ? (
          <button
            className="rounded-full border border-black/10 px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:bg-emerald-50 hover:border-emerald-200 hover:text-emerald-700"
            data-testid="publish-post-button"
            onClick={() => onPublish(post.id)}
            type="button"
          >
            Publish
          </button>
        ) : null}
        <Link
          className="flex items-center gap-1.5 rounded-full border border-black/10 px-3 py-1.5 text-xs font-medium text-ink-700 transition hover:bg-black/[0.04]"
          data-testid="edit-post-link"
          href={`/storytelling/blog/${post.id}`}
        >
          <Pencil className="size-3" />
          Edit
        </Link>
        <button
          className="rounded-full p-1.5 text-ink-400 transition hover:bg-red-50 hover:text-red-600"
          data-testid="delete-post-button"
          onClick={() => onDelete(post.id)}
          type="button"
        >
          <Trash2 className="size-4" />
        </button>
      </div>
    </article>
  );
}

export default function BlogDashboardPage() {
  const { user } = useSession();
  const queryClient = useQueryClient();

  const { data: posts = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ["author-blog-posts", user?.id],
    queryFn: () => fetchAuthorBlogPosts(user!.id),
    enabled: !!user?.id,
  });

  const { mutate: doDelete } = useMutation({
    mutationFn: (id: number) => deleteBlogPost(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["author-blog-posts"] }),
  });

  const { mutate: doPublish } = useMutation({
    mutationFn: (id: number) => publishBlogPost(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["author-blog-posts"] }),
  });

  const drafts = posts.filter((p) => p.status !== "published");
  const published = posts.filter((p) => p.status === "published");

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <PageHeader
          description="Manage your blog posts — drafts, published articles, and media."
          eyebrow="Storytelling"
          title="Blog"
        />
        <div className="mt-1 flex shrink-0 items-center gap-2">
          <Link
            className="rounded-full border border-black/10 px-3 py-2 text-sm font-medium text-ink-700 transition hover:bg-black/[0.04]"
            href="/storytelling/blog/media"
          >
            Media
          </Link>
          <Link
            className="flex items-center gap-2 rounded-full bg-ink-900 px-4 py-2.5 text-sm font-medium text-paper shadow-sm transition hover:bg-ink-700"
            href="/storytelling/blog/new"
          >
            <Plus className="size-4" />
            New post
          </Link>
        </div>
      </div>

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try refreshing the page."}
          onRetry={() => void refetch()}
          retryLabel="Reload posts"
          title="Blog posts could not be loaded."
        />
      ) : posts.length === 0 ? (
        <div
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
          data-testid="blog-empty-state"
        >
          <FileText className="size-8 text-ink-400" />
          <p className="mt-3 text-sm font-medium text-ink-700">No blog posts yet</p>
          <p className="mt-1 text-sm text-ink-500">Create your first post to start sharing your writing.</p>
          <Link
            className="mt-6 flex items-center gap-2 rounded-full bg-ink-900 px-4 py-2.5 text-sm font-medium text-paper shadow-sm transition hover:bg-ink-700"
            href="/storytelling/blog/new"
          >
            <Plus className="size-4" />
            New post
          </Link>
        </div>
      ) : (
        <div className="space-y-10">
          {drafts.length > 0 ? (
            <section className="space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Drafts</h2>
              <div className="space-y-3" data-testid="blog-drafts-list">
                {drafts.map((p) => (
                  <PostRow key={p.id} onDelete={doDelete} onPublish={doPublish} post={p} />
                ))}
              </div>
            </section>
          ) : null}

          {published.length > 0 ? (
            <section className="space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Published</h2>
              <div className="space-y-3" data-testid="blog-published-list">
                {published.map((p) => (
                  <PostRow key={p.id} onDelete={doDelete} onPublish={doPublish} post={p} />
                ))}
              </div>
            </section>
          ) : null}
        </div>
      )}
    </div>
  );
}
