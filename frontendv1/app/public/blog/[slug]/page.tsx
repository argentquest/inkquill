"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, MessageCircle, Send } from "lucide-react";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { createBlogComment, fetchBlogComments, fetchBlogPost, type BlogComment } from "@/lib/api";

function CommentCard({ comment }: { comment: BlogComment }) {
  return (
    <article className="rounded-2xl border border-black/10 bg-white/80 p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400 text-xs font-bold">
          {(comment.author?.username ?? "?").charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 text-xs text-ink-500">
            <span className="font-medium text-ink-700">{comment.author?.display_name ?? comment.author?.username ?? "Unknown"}</span>
            <span>·</span>
            <span>{new Date(comment.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
          </div>
          <p className="mt-2 text-sm text-ink-800">{comment.content}</p>
          {comment.replies && comment.replies.length > 0 ? (
            <div className="mt-3 space-y-2 border-l-2 border-black/5 pl-4">
              {comment.replies.map((reply) => (
                <CommentCard key={reply.id} comment={reply} />
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </article>
  );
}

function CommentComposer({ postId }: { postId: number }) {
  const [draft, setDraft] = useState("");
  const queryClient = useQueryClient();

  const { mutate, isPending, isError, error } = useMutation({
    mutationFn: (content: string) => createBlogComment(postId, content),
    onSuccess: () => {
      setDraft("");
      void queryClient.invalidateQueries({ queryKey: ["blog-comments", postId] });
    },
  });

  return (
    <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-sm" data-testid="comment-composer">
      <h2 className="text-sm font-semibold text-ink-900">Leave a comment</h2>
      <form
        className="mt-4 space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          const text = draft.trim();
          if (text) mutate(text);
        }}
      >
        <textarea
          className="w-full min-h-24 rounded-2xl border border-black/10 bg-[#fcfaf6] px-4 py-3 text-sm leading-7 text-ink-900 outline-none transition focus:border-amber-600 disabled:opacity-50"
          data-testid="comment-input"
          disabled={isPending}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Write your comment…"
          value={draft}
        />
        {isError ? (
          <p className="text-xs text-red-600">{error instanceof Error ? error.message : "Failed to post comment."}</p>
        ) : null}
        <div className="flex justify-end">
          <Button className="gap-2" disabled={isPending || !draft.trim()} type="submit">
            {isPending ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
            {isPending ? "Posting…" : "Post comment"}
          </Button>
        </div>
      </form>
    </section>
  );
}

export default function BlogPostPage() {
  const params = useParams();
  const slug = String(params.slug);

  const { data: post, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["blog-post", slug],
    queryFn: () => fetchBlogPost(slug),
    enabled: !!slug,
  });

  const postId = post?.id;

  const {
    data: comments,
    isLoading: commentsLoading,
    isError: commentsError,
    refetch: refetchComments,
  } = useQuery({
    queryKey: ["blog-comments", postId],
    queryFn: () => fetchBlogComments(postId!),
    enabled: !!postId,
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
          {post.comment_count > 0 ? (
            <span className="flex items-center gap-1">
              <MessageCircle className="size-3.5" />
              {post.comment_count} {post.comment_count === 1 ? "comment" : "comments"}
            </span>
          ) : null}
        </div>
      </header>

      <div
        className="prose prose-ink max-w-none text-ink-800"
        dangerouslySetInnerHTML={{ __html: post.content }}
        data-testid="blog-post-content"
      />

      <div className="border-t border-black/5 pt-8 space-y-6">
        <h2 className="text-lg font-semibold text-ink-900">Comments</h2>

        {commentsLoading ? (
          <div className="flex h-32 items-center justify-center">
            <Loader2 className="size-5 animate-spin text-ink-500" />
          </div>
        ) : commentsError ? (
          <ErrorState
            detail="Could not load comments."
            onRetry={() => void refetchComments()}
            retryLabel="Reload comments"
            title="Comments unavailable."
          />
        ) : comments && comments.length > 0 ? (
          <section className="space-y-3" data-testid="blog-comments">
            {comments.map((comment) => (
              <CommentCard key={comment.id} comment={comment} />
            ))}
          </section>
        ) : (
          <section className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-8 text-center shadow-sm">
            <p className="text-sm text-ink-500">No comments yet. Be the first to comment.</p>
          </section>
        )}

        {postId ? <CommentComposer postId={postId} /> : null}
      </div>
    </article>
  );
}
