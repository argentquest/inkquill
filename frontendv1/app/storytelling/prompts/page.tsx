"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BookOpen, Loader2, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import {
  createPrompt,
  deletePrompt,
  fetchMyPrompts,
  fetchSharedPrompts,
  type PromptEntry,
} from "@/lib/api";

const PROMPT_TYPES = [
  { value: "GENERAL", label: "General" },
  { value: "STORY", label: "Story" },
  { value: "CHARACTER", label: "Character" },
  { value: "WORLD", label: "World building" },
  { value: "SCENE", label: "Scene" },
];

function PromptCard({
  prompt,
  onDelete,
  isOwned,
}: {
  prompt: PromptEntry;
  onDelete?: (id: number) => void;
  isOwned: boolean;
}) {
  return (
    <article
      className="rounded-2xl border border-black/10 bg-white/80 p-5 shadow-sm"
      data-testid="prompt-card"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-black/[0.05] px-2 py-0.5 text-xs font-medium text-ink-700">
              {PROMPT_TYPES.find((t) => t.value === prompt.prompt_type)?.label ?? prompt.prompt_type}
            </span>
            {!prompt.is_active ? (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700">
                Inactive
              </span>
            ) : null}
          </div>
          <h3 className="mt-2 text-sm font-semibold text-ink-900">{prompt.title}</h3>
          <p className="mt-2 line-clamp-3 text-sm leading-6 text-ink-700">{prompt.prompt_content}</p>
          {prompt.reason_to_use ? (
            <p className="mt-2 text-xs text-ink-500">
              <span className="font-medium">When to use:</span> {prompt.reason_to_use}
            </p>
          ) : null}
        </div>
        {isOwned && onDelete ? (
          <button
            className="shrink-0 rounded-full p-1.5 text-ink-400 transition hover:bg-red-50 hover:text-red-600"
            data-testid="delete-prompt-button"
            onClick={() => onDelete(prompt.id)}
            type="button"
          >
            <Trash2 className="size-4" />
          </button>
        ) : null}
      </div>
    </article>
  );
}

function NewPromptForm({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [type, setType] = useState("GENERAL");
  const [reason, setReason] = useState("");

  const { mutate, isPending, isError, error } = useMutation({
    mutationFn: () => createPrompt({ title, prompt_content: content, prompt_type: type, reason_to_use: reason || undefined }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["my-prompts"] });
      onClose();
    },
  });

  return (
    <div className="rounded-[28px] border border-black/10 bg-white/90 p-6 shadow-panel" data-testid="new-prompt-form">
      <h2 className="text-base font-semibold text-ink-900">New prompt</h2>
      <form
        className="mt-4 space-y-4"
        onSubmit={(e) => {
          e.preventDefault();
          if (title.trim() && content.trim()) mutate();
        }}
      >
        <div className="space-y-1">
          <label className="block text-xs font-medium text-ink-700" htmlFor="prompt-title">Title</label>
          <input
            className="w-full rounded-xl border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-900 outline-none focus:border-amber-600"
            disabled={isPending}
            id="prompt-title"
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Give your prompt a short name"
            value={title}
          />
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-ink-700" htmlFor="prompt-type">Type</label>
          <select
            className="w-full rounded-xl border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-900 outline-none focus:border-amber-600"
            disabled={isPending}
            id="prompt-type"
            onChange={(e) => setType(e.target.value)}
            value={type}
          >
            {PROMPT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-ink-700" htmlFor="prompt-content">Prompt content</label>
          <textarea
            className="w-full min-h-28 rounded-xl border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm leading-6 text-ink-900 outline-none focus:border-amber-600 disabled:opacity-50"
            disabled={isPending}
            id="prompt-content"
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write the prompt text…"
            value={content}
          />
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-ink-700" htmlFor="prompt-reason">When to use (optional)</label>
          <input
            className="w-full rounded-xl border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-900 outline-none focus:border-amber-600"
            disabled={isPending}
            id="prompt-reason"
            onChange={(e) => setReason(e.target.value)}
            placeholder="Brief description of when this prompt is useful"
            value={reason}
          />
        </div>
        {isError ? (
          <p className="text-xs text-red-600">{error instanceof Error ? error.message : "Failed to create prompt."}</p>
        ) : null}
        <div className="flex items-center justify-between gap-4">
          <button className="text-sm text-ink-500 hover:text-ink-900" onClick={onClose} type="button">Cancel</button>
          <Button disabled={isPending || !title.trim() || !content.trim()} type="submit">
            {isPending ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
            Save prompt
          </Button>
        </div>
      </form>
    </div>
  );
}

export default function PromptsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);

  const { data: myPrompts = [], isLoading: myLoading, isError: myError, error: myErr, refetch: refetchMy } = useQuery({
    queryKey: ["my-prompts"],
    queryFn: fetchMyPrompts,
  });

  const { data: sharedPrompts = [], isLoading: sharedLoading } = useQuery({
    queryKey: ["shared-prompts"],
    queryFn: fetchSharedPrompts,
  });

  const { mutate: doDelete } = useMutation({
    mutationFn: (id: number) => deletePrompt(id),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["my-prompts"] }),
  });

  const isLoading = myLoading || sharedLoading;

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <PageHeader
          description="Save and reuse custom prompts for story generation, world building, and scene writing."
          eyebrow="Storytelling"
          title="Prompt Library"
        />
        <Button
          className="mt-1 shrink-0 gap-2"
          data-testid="new-prompt-button"
          onClick={() => setShowForm(true)}
        >
          <Plus className="size-4" />
          New prompt
        </Button>
      </div>

      {showForm ? (
        <NewPromptForm onClose={() => setShowForm(false)} />
      ) : null}

      {isLoading ? (
        <div className="flex h-32 items-center justify-center">
          <Loader2 className="size-6 animate-spin text-ink-500" />
        </div>
      ) : myError ? (
        <ErrorState
          detail={myErr instanceof Error ? myErr.message : "Try refreshing the page."}
          onRetry={() => void refetchMy()}
          retryLabel="Reload prompts"
          title="Prompts could not be loaded."
        />
      ) : (
        <div className="space-y-10">
          <section className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">My prompts</h2>
            {myPrompts.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2" data-testid="my-prompts-list">
                {myPrompts.map((p) => (
                  <PromptCard isOwned key={p.id} onDelete={(id) => doDelete(id)} prompt={p} />
                ))}
              </div>
            ) : (
              <div
                className="flex flex-col items-center justify-center rounded-[28px] border-2 border-dashed border-black/10 bg-white/50 p-12 text-center shadow-sm"
                data-testid="my-prompts-empty"
              >
                <BookOpen className="size-8 text-ink-400" />
                <p className="mt-3 text-sm font-medium text-ink-700">No prompts yet</p>
                <p className="mt-1 text-sm text-ink-500">Create your first prompt to speed up your writing workflow.</p>
              </div>
            )}
          </section>

          {sharedPrompts.length > 0 ? (
            <section className="space-y-4">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Shared prompts</h2>
              <div className="grid gap-4 md:grid-cols-2" data-testid="shared-prompts-list">
                {sharedPrompts.map((p) => (
                  <PromptCard isOwned={false} key={p.id} prompt={p} />
                ))}
              </div>
            </section>
          ) : null}
        </div>
      )}
    </div>
  );
}
