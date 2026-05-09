"use client";

import Link from "next/link";
import type { BlogPost, ForumThreadSummary } from "@/lib/api";
import { SectionHeading } from "@/components/shell/section-heading";

export function HubSidebar({
  blogPosts = [],
  forumThreads = [],
  blogHref,
  forumHref,
}: {
  blogPosts?: BlogPost[];
  forumThreads?: ForumThreadSummary[];
  blogHref?: string;
  forumHref?: string;
}) {
  if (!blogPosts.length && !forumThreads.length) return null;

  return (
    <aside className="space-y-6">
      {blogPosts.length > 0 && (
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-5 shadow-panel">
          <SectionHeading
            title="Blog"
            action={blogHref ? { label: "All posts", href: blogHref } : undefined}
          />
          <ul className="mt-4 space-y-2">
            {blogPosts.slice(0, 4).map((post) => (
              <li key={post.id}>
                <Link
                  href={`/public/blog/${post.slug}`}
                  className="block rounded-2xl border border-black/10 bg-white/70 px-4 py-3 transition hover:border-black/20"
                >
                  <p className="text-sm font-semibold leading-5 text-ink-900">{post.title}</p>
                  <p className="mt-0.5 text-xs text-ink-500">
                    {post.comment_count} comments · {post.view_count.toLocaleString()} views
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
      {forumThreads.length > 0 && (
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-5 shadow-panel">
          <SectionHeading
            title="Forum"
            action={forumHref ? { label: "All threads", href: forumHref } : undefined}
          />
          <ul className="mt-4 space-y-2">
            {forumThreads.slice(0, 4).map((thread) => (
              <li key={thread.id}>
                <Link
                  href={`/community/forums/${thread.id}`}
                  className="block rounded-2xl border border-black/10 bg-white/70 px-4 py-3 transition hover:border-black/20"
                >
                  <p className="text-sm font-semibold leading-5 text-ink-900">{thread.title}</p>
                  <p className="mt-0.5 text-xs text-ink-500">
                    {thread.category_name ?? "Forum"} · {thread.post_count} replies
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </aside>
  );
}
