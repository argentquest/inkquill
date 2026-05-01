"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BookOpen, FileText, Loader2, MessageSquare, Search, Share2, Sparkles } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { PageHeader } from "@/components/shell/page-header";
import { ErrorState } from "@/components/ui/error-state";
import { fetchBlogPosts, fetchForumThreads, fetchPublishedStories } from "@/lib/api";

function HubCard({
  title,
  description,
  href,
  icon,
}: {
  title: string;
  description: string;
  href: string;
  icon: ReactNode;
}) {
  return (
    <Link
      className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel transition hover:-translate-y-0.5 hover:shadow-md"
      href={href}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-paper text-ink-500 shadow-sm">
            {icon}
          </div>
          <div>
            <h2 className="text-base font-semibold text-ink-900">{title}</h2>
            <p className="mt-1 text-sm leading-6 text-ink-600">{description}</p>
          </div>
        </div>
        <ArrowRight className="mt-2 size-5 shrink-0 text-ink-400" />
      </div>
    </Link>
  );
}

export default function CommunityPage() {
  const {
    data: publishedData,
    isLoading: storiesLoading,
    isError: storiesError,
    error: storiesErr,
    refetch: refetchStories,
  } = useQuery({
    queryKey: ["community-published-stories"],
    queryFn: () => fetchPublishedStories({ sort_by: "recent", per_page: 3 }),
  });

  const { data: forumThreads = [], isLoading: forumLoading } = useQuery({
    queryKey: ["community-forum-threads"],
    queryFn: () => fetchForumThreads(),
  });

  const { data: blogPosts = [], isLoading: blogLoading } = useQuery({
    queryKey: ["community-blog-posts"],
    queryFn: () => fetchBlogPosts(),
  });

  const isLoading = storiesLoading || forumLoading || blogLoading;
  const stories = publishedData?.stories ?? [];

  return (
    <div className="space-y-8" data-testid="storytelling-community-hub">
      <PageHeader
        description="Keep your public presence moving with reading, discussion, and discovery routes that connect back to your storytelling workspace."
        eyebrow="Community"
        title="Storytelling Community"
      />

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[32px] border border-black/10 bg-[linear-gradient(135deg,rgba(248,243,232,0.95),rgba(255,255,255,0.95))] p-8 shadow-panel">
          <div className="max-w-2xl space-y-4">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-ink-500">
              <Sparkles className="size-3.5" />
              Publish and connect
            </div>
            <h2 className="font-serif text-3xl text-ink-900">Move from private drafting into public readership.</h2>
            <p className="max-w-xl text-sm leading-7 text-ink-600">
              Use this hub to jump between published stories, community forums, public blog content, and discovery search without dropping back into legacy templates.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
          <div className="rounded-[28px] border border-black/10 bg-white/80 p-5 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink-500">Published</p>
            <p className="mt-3 text-3xl font-semibold text-ink-900">{stories.length}</p>
            <p className="mt-1 text-sm text-ink-600">Recent public stories surfaced for readers.</p>
          </div>
          <div className="rounded-[28px] border border-black/10 bg-white/80 p-5 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink-500">Forum</p>
            <p className="mt-3 text-3xl font-semibold text-ink-900">{forumThreads.slice(0, 10).length}</p>
            <p className="mt-1 text-sm text-ink-600">Visible discussion threads available to browse now.</p>
          </div>
          <div className="rounded-[28px] border border-black/10 bg-white/80 p-5 shadow-panel">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-ink-500">Blog</p>
            <p className="mt-3 text-3xl font-semibold text-ink-900">{blogPosts.length}</p>
            <p className="mt-1 text-sm text-ink-600">Public posts that support announcements and discovery.</p>
          </div>
        </div>
      </section>

      {storiesError ? (
        <ErrorState
          detail={storiesErr instanceof Error ? storiesErr.message : "Try refreshing the community hub."}
          onRetry={() => void refetchStories()}
          retryLabel="Reload community"
          title="Community data could not be loaded."
        />
      ) : isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <HubCard
              description="Browse the live public catalog and jump into individual reader pages."
              href="/public/published-stories"
              icon={<BookOpen className="size-5" />}
              title="Published Stories"
            />
            <HubCard
              description="See category-level discussion and read active writer threads."
              href="/community/forums"
              icon={<MessageSquare className="size-5" />}
              title="Forums"
            />
            <HubCard
              description="Read public announcements, editorial posts, and product updates."
              href="/public/blog"
              icon={<FileText className="size-5" />}
              title="Blog"
            />
            <HubCard
              description="Search public writing content and guides from one route."
              href="/public/search"
              icon={<Search className="size-5" />}
              title="Discovery Search"
            />
          </section>

          <section className="grid gap-6 xl:grid-cols-3">
            <div className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
              <div className="flex items-center gap-2 text-sm font-semibold text-ink-900">
                <BookOpen className="size-4 text-ink-500" />
                Freshly published
              </div>
              <div className="mt-4 space-y-3">
                {stories.length ? (
                  stories.map((story) => (
                    <Link
                      key={story.id}
                      className="block rounded-2xl border border-black/10 bg-white/70 p-4 transition hover:border-black/20"
                      href={`/public/stories/${story.id}`}
                    >
                      <p className="text-sm font-semibold text-ink-900">{story.title}</p>
                      <p className="mt-1 text-xs text-ink-500">
                        {story.publisher_display_name ?? story.publisher_username ?? "Anonymous"} • {story.view_count.toLocaleString()} views
                      </p>
                    </Link>
                  ))
                ) : (
                  <p className="text-sm text-ink-500">No published stories are available yet.</p>
                )}
              </div>
            </div>

            <div className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
              <div className="flex items-center gap-2 text-sm font-semibold text-ink-900">
                <MessageSquare className="size-4 text-ink-500" />
                Active discussions
              </div>
              <div className="mt-4 space-y-3">
                {forumThreads.slice(0, 3).length ? (
                  forumThreads.slice(0, 3).map((thread) => (
                    <Link
                      key={thread.id}
                      className="block rounded-2xl border border-black/10 bg-white/70 p-4 transition hover:border-black/20"
                      href={`/community/forums/${thread.id}`}
                    >
                      <p className="text-sm font-semibold text-ink-900">{thread.title}</p>
                      <p className="mt-1 text-xs text-ink-500">
                        {thread.category_name ?? "Forum"} • {thread.post_count} replies
                      </p>
                    </Link>
                  ))
                ) : (
                  <p className="text-sm text-ink-500">No public threads are visible yet.</p>
                )}
              </div>
            </div>

            <div className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
              <div className="flex items-center gap-2 text-sm font-semibold text-ink-900">
                <Share2 className="size-4 text-ink-500" />
                Discovery loop
              </div>
              <div className="mt-4 space-y-3">
                {blogPosts.slice(0, 3).length ? (
                  blogPosts.slice(0, 3).map((post) => (
                    <Link
                      key={post.id}
                      className="block rounded-2xl border border-black/10 bg-white/70 p-4 transition hover:border-black/20"
                      href={`/public/blog/${post.slug}`}
                    >
                      <p className="text-sm font-semibold text-ink-900">{post.title}</p>
                      <p className="mt-1 text-xs text-ink-500">{post.comment_count} comments • {post.view_count.toLocaleString()} views</p>
                    </Link>
                  ))
                ) : (
                  <p className="text-sm text-ink-500">No public blog posts are available yet.</p>
                )}
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
