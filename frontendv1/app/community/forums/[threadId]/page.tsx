"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowDown, ArrowUp, Loader2, MessageSquare, Pin, Send } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import { useSession } from "@/components/providers/app-providers";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { RichTextEditor } from "@/components/ui/rich-text-editor";
import { createForumPost, fetchForumThread, voteForumPost, type ForumPost } from "@/lib/api";

function VoteBar({ post, threadId }: { post: ForumPost; threadId: number }) {
  const session = useSession();
  const isAuthenticated = session.status === "authenticated";
  const queryClient = useQueryClient();
  const [optimisticVote, setOptimisticVote] = useState<"upvote" | "downvote" | null>(post.user_vote ?? null);
  const [optimisticUp, setOptimisticUp] = useState(post.upvote_count);
  const [optimisticDown, setOptimisticDown] = useState(post.downvote_count);

  const { mutate, isPending } = useMutation({
    mutationFn: (voteType: "upvote" | "downvote") => voteForumPost(post.id, voteType),
    onSuccess: (data) => {
      setOptimisticVote(data.user_vote as "upvote" | "downvote");
      setOptimisticUp(data.upvote_count);
      setOptimisticDown(data.downvote_count);
      void queryClient.invalidateQueries({ queryKey: ["forum-thread", threadId] });
    },
  });

  const handleVote = (voteType: "upvote" | "downvote") => {
    if (!isAuthenticated) {
      window.location.href = `/auth/login?next=${encodeURIComponent(window.location.pathname)}`;
      return;
    }
    mutate(voteType);
  };

  return (
    <div className="flex items-center gap-1" data-testid={`post-votes-${post.id}`}>
      <button
        className={`flex items-center gap-0.5 rounded-lg px-2 py-1 text-xs transition ${
          optimisticVote === "upvote" ? "bg-amber-100 text-amber-700" : "text-ink-500 hover:bg-black/[0.03]"
        }`}
        disabled={isPending}
        onClick={() => handleVote("upvote")}
        title={isAuthenticated ? undefined : "Sign in to vote"}
        type="button"
      >
        <ArrowUp className="size-3" />
        {optimisticUp}
      </button>
      <button
        className={`flex items-center gap-0.5 rounded-lg px-2 py-1 text-xs transition ${
          optimisticVote === "downvote" ? "bg-red-100 text-red-700" : "text-ink-500 hover:bg-black/[0.03]"
        }`}
        disabled={isPending}
        onClick={() => handleVote("downvote")}
        title={isAuthenticated ? undefined : "Sign in to vote"}
        type="button"
      >
        <ArrowDown className="size-3" />
        {optimisticDown}
      </button>
    </div>
  );
}

function PostCard({ post, threadId }: { post: ForumPost; threadId: number }) {
  return (
    <article
      className={`rounded-2xl border p-5 shadow-sm ${post.is_deleted ? "border-black/5 bg-white/40 opacity-60" : "border-black/10 bg-white/80"}`}
      data-testid={`post-card-${post.id}`}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400 text-xs font-bold">
          {post.username.charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 text-xs text-ink-500">
            <span className="font-medium text-ink-700">{post.user_display_name ?? post.username}</span>
            <span>·</span>
            <span>{new Date(post.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
          </div>
          {post.is_deleted ? (
            <p className="mt-2 text-sm italic text-ink-400">This post has been deleted.</p>
          ) : post.content_html ? (
            <div
              className="prose prose-sm prose-ink mt-2 max-w-none text-ink-800"
              dangerouslySetInnerHTML={{ __html: post.content_html }}
            />
          ) : (
            <p className="mt-2 text-sm text-ink-800">{post.content}</p>
          )}
          <div className="mt-3 flex items-center gap-4">
            <VoteBar post={post} threadId={threadId} />
          </div>
        </div>
      </div>
    </article>
  );
}

function ReplyComposer({ threadId, isLocked }: { threadId: number; isLocked: boolean }) {
  const session = useSession();
  const isAuthenticated = session.status === "authenticated";
  const [draft, setDraft] = useState("");
  const queryClient = useQueryClient();

  const { mutate: submitReply, isPending, isError, error } = useMutation({
    mutationFn: (html: string) =>
      createForumPost({
        thread_id: threadId,
        content: html.replace(/<[^>]*>/g, "").trim(),
        content_html: html,
      }),
    onSuccess: () => {
      setDraft("");
      void queryClient.invalidateQueries({ queryKey: ["forum-thread", threadId] });
    },
  });

  if (isLocked) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700" data-testid="thread-locked-notice">
        This thread is locked. No new replies can be posted.
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <section
        className="flex flex-col items-center gap-3 rounded-[28px] border border-black/10 bg-white/80 p-8 text-center shadow-sm"
        data-testid="reply-signin-prompt"
      >
        <MessageSquare className="size-8 text-ink-300" />
        <p className="text-sm font-medium text-ink-700">Sign in to join the discussion</p>
        <p className="text-xs text-ink-500">You need an account to post replies and vote on posts.</p>
        <Link
          className="mt-1 rounded-full bg-ink-900 px-5 py-2 text-sm font-medium text-paper transition hover:bg-ink-700"
          href={`/auth/login?next=${encodeURIComponent(typeof window !== "undefined" ? window.location.pathname : "")}`}
        >
          Sign in
        </Link>
      </section>
    );
  }

  const draftIsEmpty = draft.replace(/<[^>]*>/g, "").trim().length === 0;

  return (
    <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-sm" data-testid="reply-composer">
      <h2 className="text-sm font-semibold text-ink-900">Post a reply</h2>
      <div className="mt-4 space-y-3">
        <RichTextEditor
          disabled={isPending}
          minHeight="6rem"
          onChange={setDraft}
          placeholder="Write your reply…"
          value={draft}
          variant="compact"
        />
        {isError ? (
          <p className="text-xs text-red-600">{error instanceof Error ? error.message : "Failed to post reply."}</p>
        ) : null}
        <div className="flex justify-end">
          <Button
            className="gap-2"
            disabled={isPending || draftIsEmpty}
            onClick={() => { if (!draftIsEmpty) submitReply(draft); }}
            type="button"
          >
            {isPending ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
            {isPending ? "Posting…" : "Post reply"}
          </Button>
        </div>
      </div>
    </section>
  );
}

export default function ForumThreadPage() {
  const params = useParams();
  const threadId = Number(params.threadId);

  const { data: thread, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["forum-thread", threadId],
    queryFn: () => fetchForumThread(threadId),
    enabled: !isNaN(threadId),
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !thread) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "The thread may have been deleted or moved."}
        onRetry={() => void refetch()}
        retryLabel="Reload thread"
        title="Thread could not be loaded."
      />
    );
  }

  const visiblePosts = thread.posts ?? [];

  return (
    <div className="space-y-6" data-testid="forum-thread">
      <header className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400 shadow-sm">
            <MessageSquare className="size-6" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              {thread.is_pinned ? (
                <Pin className="size-4 text-ink-500" />
              ) : null}
              {thread.category_name ? (
                <span className="rounded-full bg-black/[0.05] px-2.5 py-0.5 text-xs font-medium text-ink-700">
                  {thread.category_name}
                </span>
              ) : null}
            </div>
            <h1 className="mt-1 text-xl font-bold text-ink-900">{thread.title}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-ink-500">
              <span>by {thread.username}</span>
              <span>{thread.post_count} {thread.post_count === 1 ? "reply" : "replies"}</span>
              <span>{thread.view_count.toLocaleString()} views</span>
              {thread.is_locked ? <span className="font-medium text-amber-600">Locked</span> : null}
            </div>
          </div>
        </div>
      </header>

      {visiblePosts.length > 0 ? (
        <section className="space-y-3" data-testid="thread-posts">
          {visiblePosts.map((post) => (
            <PostCard key={post.id} post={post} threadId={threadId} />
          ))}
        </section>
      ) : (
        <section className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-12 text-center shadow-sm">
          <p className="text-sm text-ink-500">No replies yet. Be the first to reply.</p>
        </section>
      )}

      <ReplyComposer isLocked={thread.is_locked} threadId={threadId} />
    </div>
  );
}
