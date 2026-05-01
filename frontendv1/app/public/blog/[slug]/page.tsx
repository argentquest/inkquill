"use client";

import { useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { useParams } from "next/navigation";

import { ErrorState } from "@/components/ui/error-state";
import { fetchBlogPost } from "@/lib/api";

export default function BlogPostPage() {
  const params = useParams();
  const slug = String(params.slug);

  const { data: post, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["blog-post", slug],
    queryFn: () => fetchBlogPost(slug),
    enabled: !!slug,
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !post) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "The post may have been removed or unpublished."}
        onRetry={() => void refetch()}
        retryLabel="Reload post"
        title="Blog post could not be loaded."
      />
    );
  }

  const publishedDate = post.published_at
    ? new Date(post.published_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
    : null;

  return (
    <article className="mx-auto max-w-2xl space-y-8" data-testid="blog-post">
      <header className="space-y-4">
        {post.featured_image_url ? (
          <div className="overflow-hidden rounded-[28px]">
            <img
              alt={post.title}
              className="h-64 w-full object-cover"
              src={post.featured_image_url}
            />
          </div>
        ) : null}
        <h1 className="text-3xl font-bold text-ink-900">{post.title}</h1>
        {post.excerpt ? (
          <p className="text-lg text-ink-600">{post.excerpt}</p>
        ) : null}
        <div className="flex flex-wrap items-center gap-4 text-sm text-ink-500 border-b border-black/5 pb-4">
          {publishedDate ? <span>{publishedDate}</span> : null}
          <span>{post.view_count.toLocaleString()} views</span>
        </div>
      </header>

      <div
        className="prose prose-ink max-w-none text-ink-800"
        dangerouslySetInnerHTML={{ __html: post.content }}
        data-testid="blog-post-content"
      />
    </article>
  );
}
