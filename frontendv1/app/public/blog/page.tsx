"use client";

import { useQuery } from "@tanstack/react-query";
import { FileText, Loader2 } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { fetchBlogPosts, type BlogPost } from "@/lib/api";

function BlogCard({ post }: { post: BlogPost }) {
  const publishedDate = post.published_at
    ? new Date(post.published_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
    : null;

  return (
    <Link href={`/public/blog/${post.slug}`}>
      <article className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel transition-shadow hover:shadow-md">
        {post.featured_image_url ? (
          <div className="mb-4 overflow-hidden rounded-2xl">
            <img
              alt={post.title}
              className="h-40 w-full object-cover"
              src={post.featured_image_url}
            />
          </div>
        ) : null}
        <div className="space-y-2">
          <h2 className="text-base font-semibold text-ink-900 line-clamp-2">{post.title}</h2>
          {post.excerpt ? (
            <p className="text-sm leading-6 text-ink-600 line-clamp-3">{post.excerpt}</p>
          ) : null}
          <div className="flex flex-wrap items-center gap-3 pt-1 text-xs text-ink-500">
            {publishedDate ? <span>{publishedDate}</span> : null}
            <span>{post.view_count.toLocaleString()} views</span>
          </div>
        </div>
      </article>
    </Link>
  );
}

export default function BlogListPage() {
  const { data: posts = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ["blog-posts"],
    queryFn: () => fetchBlogPosts(),
  });

  return (
    <div className="space-y-8">
      <PageHeader
        description="Articles, announcements, and guides from the Ink and Quill team."
        eyebrow="Blog"
        title="Blog"
      />

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
      ) : !posts.length ? (
        <section
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
          data-testid="blog-empty-state"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <FileText className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No posts yet</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">
            Blog posts will appear here once they are published.
          </p>
        </section>
      ) : (
        <section className="space-y-4" data-testid="blog-list">
          <p className="text-sm text-ink-600">
            {posts.length} {posts.length === 1 ? "post" : "posts"}
          </p>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {posts.map((post) => (
              <BlogCard key={post.id} post={post} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
