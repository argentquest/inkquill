"use client";

import { useQuery } from "@tanstack/react-query";
import { FileText, Loader2, Search } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { ErrorState } from "@/components/ui/error-state";
import { fetchBlogSearch, type BlogPost } from "@/lib/api";

function SearchResultCard({ post }: { post: BlogPost }) {
  const publishedDate = post.published_at
    ? new Date(post.published_at).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })
    : null;

  return (
    <Link href={`/public/blog/${post.slug}`}>
      <article className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel transition-shadow hover:shadow-md">
        <div className="flex items-start gap-4">
          <div className="flex shrink-0 items-center justify-center rounded-full bg-paper p-3 text-ink-400">
            <FileText className="size-5" />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-base font-semibold text-ink-900 line-clamp-2">{post.title}</h2>
            {post.excerpt ? (
              <p className="mt-1 text-sm text-ink-600 line-clamp-2">{post.excerpt}</p>
            ) : null}
            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-ink-500">
              {publishedDate ? <span>{publishedDate}</span> : null}
              <span>{post.view_count.toLocaleString()} views</span>
            </div>
          </div>
        </div>
      </article>
    </Link>
  );
}

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") ?? "";
  const [inputValue, setInputValue] = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);

  const { data: results = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ["blog-search", activeQuery],
    queryFn: () => fetchBlogSearch(activeQuery),
    enabled: activeQuery.length >= 2,
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed) return;
    setActiveQuery(trimmed);
    router.push(`/public/search?q=${encodeURIComponent(trimmed)}`, { scroll: false });
  }

  return (
    <div className="space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-ink-900">Search</h1>
        <p className="text-ink-600">Find blog posts, guides, and platform updates.</p>
      </div>

      <form className="flex gap-3" onSubmit={handleSubmit}>
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-ink-400" />
          <input
            aria-label="Search query"
            className="w-full rounded-2xl border border-black/10 bg-white/80 py-3 pl-11 pr-4 text-sm text-ink-900 placeholder-ink-400 shadow-sm outline-none focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Search posts…"
            type="search"
            value={inputValue}
          />
        </div>
        <button
          className="rounded-2xl bg-ink-900 px-6 py-3 text-sm font-medium text-white shadow-sm hover:bg-ink-800 disabled:opacity-50"
          disabled={!inputValue.trim()}
          type="submit"
        >
          Search
        </button>
      </form>

      {activeQuery.length < 2 ? (
        <p className="text-sm text-ink-500" data-testid="search-prompt">
          Enter at least 2 characters to search.
        </p>
      ) : isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : isError ? (
        <ErrorState
          detail={error instanceof Error ? error.message : "Try a different search term."}
          onRetry={() => void refetch()}
          retryLabel="Retry search"
          title="Search failed."
        />
      ) : !results.length ? (
        <section
          className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-16 text-center shadow-sm"
          data-testid="search-no-results"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            <Search className="size-8" />
          </div>
          <h3 className="mt-4 text-base font-bold text-ink-900">No results for &quot;{activeQuery}&quot;</h3>
          <p className="mt-2 max-w-sm text-sm text-ink-500">Try different keywords or a broader search term.</p>
        </section>
      ) : (
        <section className="space-y-4" data-testid="search-results">
          <p className="text-sm text-ink-600">
            {results.length} {results.length === 1 ? "result" : "results"} for &quot;{activeQuery}&quot;
          </p>
          <div className="space-y-3">
            {results.map((post) => (
              <SearchResultCard key={post.id} post={post} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="flex h-32 items-center justify-center"><Loader2 className="size-6 animate-spin text-ink-500" /></div>}>
      <SearchContent />
    </Suspense>
  );
}
