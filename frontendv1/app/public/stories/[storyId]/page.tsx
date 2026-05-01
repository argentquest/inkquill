"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Loader2, MessageSquare, Send, Share2, Star } from "lucide-react";
import { useParams } from "next/navigation";
import { useState } from "react";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { createStoryComment, fetchPublishedStory, fetchStoryComments, ratePublishedStory } from "@/lib/api";

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="flex items-center gap-1 text-sm text-ink-600">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          className={`size-4 ${i < Math.round(rating) ? "fill-amber-400 text-amber-400" : "text-ink-300"}`}
        />
      ))}
      <span className="ml-1">{rating.toFixed(1)}</span>
    </span>
  );
}

export default function PublishedStoryReaderPage() {
  const params = useParams();
  const storyId = Number(params.storyId);
  const queryClient = useQueryClient();
  const { status } = useSession();
  const { pushToast } = useToasts();
  const [commentDraft, setCommentDraft] = useState("");

  const { data: story, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["published-story", storyId],
    queryFn: () => fetchPublishedStory(storyId),
    enabled: !isNaN(storyId),
  });

  const { data: comments = [] } = useQuery({
    queryKey: ["story-comments", storyId],
    queryFn: () => fetchStoryComments(storyId),
    enabled: !isNaN(storyId) && !!story,
  });

  const rateMutation = useMutation({
    mutationFn: (rating: number) => ratePublishedStory(storyId, rating),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["published-story", storyId] }),
        queryClient.invalidateQueries({ queryKey: ["published-stories"] }),
      ]);
      pushToast({
        title: "Rating saved",
        detail: "Your rating has been added to this published story.",
        tone: "success",
      });
    },
    onError: (mutationError) => {
      pushToast({
        title: "Rating failed",
        detail: mutationError instanceof Error ? mutationError.message : "Try again in a moment.",
        tone: "warning",
      });
    },
  });

  const commentMutation = useMutation({
    mutationFn: (content: string) => createStoryComment(storyId, content),
    onSuccess: async () => {
      setCommentDraft("");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["story-comments", storyId] }),
        queryClient.invalidateQueries({ queryKey: ["published-story", storyId] }),
      ]);
      pushToast({
        title: "Comment posted",
        detail: "Your comment is now part of the public discussion.",
        tone: "success",
      });
    },
    onError: (mutationError) => {
      pushToast({
        title: "Comment failed",
        detail: mutationError instanceof Error ? mutationError.message : "Try again in a moment.",
        tone: "warning",
      });
    },
  });

  async function handleShare() {
    if (!story) {
      return;
    }

    const shareUrl = window.location.href;
    try {
      if (navigator.share) {
        await navigator.share({
          title: story.title,
          text: story.description ?? "Read this published story on Ink and Quill.",
          url: shareUrl,
        });
        pushToast({
          title: "Share sheet opened",
          detail: "Use your device's share options to send the reader link.",
          tone: "info",
        });
        return;
      }

      await navigator.clipboard.writeText(shareUrl);
      pushToast({
        title: "Link copied",
        detail: "The story link has been copied to your clipboard.",
        tone: "success",
      });
    } catch {
      pushToast({
        title: "Share canceled",
        detail: "You can still copy the page URL directly from your browser.",
        tone: "info",
      });
    }
  }

  function handleCommentSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = commentDraft.trim();
    if (!trimmed) {
      return;
    }
    commentMutation.mutate(trimmed);
  }

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (isError || !story) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : "The story may have been removed or made private."}
        onRetry={() => void refetch()}
        retryLabel="Reload story"
        title="Story could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-8" data-testid="story-reader">
      <header className="space-y-4 rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-paper text-ink-400 shadow-sm">
            <BookOpen className="size-7" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="text-2xl font-bold text-ink-900">{story.title}</h1>
            {story.description ? (
              <p className="mt-2 text-base text-ink-600">{story.description}</p>
            ) : null}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-4 border-t border-black/5 pt-4 text-sm text-ink-500">
          {story.publisher_display_name ? (
            <span>
              by <span className="font-medium text-ink-700">{story.publisher_display_name}</span>
            </span>
          ) : null}
          {story.world_name ? (
            <span className="rounded-full bg-black/[0.05] px-2.5 py-1 font-medium text-ink-700">
              {story.world_name}
            </span>
          ) : null}
          {story.word_count ? <span>{story.word_count.toLocaleString()} words</span> : null}
          <span>{story.view_count.toLocaleString()} views</span>
          {story.average_rating ? <StarRating rating={story.average_rating} /> : null}
        </div>

        <section className="grid gap-4 border-t border-black/5 pt-5 lg:grid-cols-[1.5fr_1fr]">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-ink-900">
              <Star className="size-4 text-amber-500" />
              Reader rating
            </div>
            <div className="flex flex-wrap gap-2" data-testid="story-rating-controls">
              {Array.from({ length: 5 }).map((_, index) => {
                const value = index + 1;
                const isActive = (story.user_rating ?? 0) >= value;
                return (
                  <button
                    key={value}
                    aria-label={`Rate story ${value} stars`}
                    className={`inline-flex items-center gap-1 rounded-full border px-3 py-2 text-sm font-medium transition ${
                      isActive
                        ? "border-amber-300 bg-amber-50 text-amber-700"
                        : "border-black/10 bg-white/80 text-ink-700 hover:border-amber-200 hover:bg-amber-50/60"
                    }`}
                    disabled={status !== "authenticated" || rateMutation.isPending}
                    onClick={() => rateMutation.mutate(value)}
                    type="button"
                  >
                    <Star className={`size-4 ${isActive ? "fill-amber-400 text-amber-400" : "text-ink-300"}`} />
                    {value}
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-ink-500">
              {status === "authenticated"
                ? story.has_user_rated && story.user_rating
                  ? `You rated this story ${story.user_rating} out of 5.`
                  : "Add your rating to help other readers discover strong work."
                : "Sign in to rate this story."}
            </p>
          </div>

          <div className="space-y-3 rounded-2xl border border-black/10 bg-white/60 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-ink-900">
              <Share2 className="size-4 text-ink-500" />
              Share story
            </div>
            <p className="text-sm text-ink-600">Send readers straight to this published page.</p>
            <Button className="w-full" onClick={() => void handleShare()} variant="secondary">
              <Share2 className="mr-2 size-4" />
              Share link
            </Button>
          </div>
        </section>
      </header>

      <section className="space-y-4" data-testid="story-comments">
        <div className="flex items-center gap-2 text-base font-semibold text-ink-900">
          <MessageSquare className="size-4" />
          {comments.length} {comments.length === 1 ? "Comment" : "Comments"}
        </div>

        <form className="rounded-[28px] border border-black/10 bg-white/80 p-5 shadow-panel" onSubmit={handleCommentSubmit}>
          <label className="block text-sm font-medium text-ink-900" htmlFor="story-comment">
            Join the discussion
          </label>
          <textarea
            className="mt-3 min-h-28 w-full rounded-2xl border border-black/10 bg-white px-4 py-3 text-sm text-ink-900 outline-none transition focus:border-ink-400 focus:ring-2 focus:ring-ink-200 disabled:cursor-not-allowed disabled:opacity-60"
            data-testid="story-comment-input"
            disabled={status !== "authenticated" || commentMutation.isPending}
            id="story-comment"
            onChange={(event) => setCommentDraft(event.target.value)}
            placeholder={
              status === "authenticated"
                ? "Share what landed for you in this story."
                : "Sign in to add a comment."
            }
            value={commentDraft}
          />
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-ink-500">
              {status === "authenticated"
                ? "Comments are posted publicly on the reader page."
                : "Authentication is required before posting a comment."}
            </p>
            <Button
              disabled={status !== "authenticated" || !commentDraft.trim() || commentMutation.isPending}
              type="submit"
            >
              <Send className="mr-2 size-4" />
              {commentMutation.isPending ? "Posting..." : "Post comment"}
            </Button>
          </div>
        </form>

        {comments.length > 0 ? (
          <div className="space-y-3">
            {comments.map((comment) => (
              <article
                key={comment.id}
                className="rounded-2xl border border-black/10 bg-white/80 p-4 shadow-sm"
              >
                <p className="text-sm font-medium text-ink-700">
                  {comment.commenter_display_name ?? comment.commenter_username ?? "Anonymous"}
                </p>
                <p className="mt-1 text-sm text-ink-600">{comment.content}</p>
              </article>
            ))}
          </div>
        ) : (
          <div className="rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-10 text-center shadow-sm">
            <p className="text-sm text-ink-500">No comments yet. Be the first reader to respond.</p>
          </div>
        )}
      </section>
    </div>
  );
}
