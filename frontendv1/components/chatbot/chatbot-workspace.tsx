"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Bot,
  CornerDownLeft,
  Loader2,
  MessageSquarePlus,
  RefreshCw,
  Sparkles,
  Trash2,
  User2,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  createChatbotSession,
  deleteChatbotSession,
  fetchChatbotSession,
  fetchChatbotSessions,
  sendChatbotMessage,
  type ChatbotMessage,
  type ChatbotSession,
} from "@/lib/api";

const starterPrompts = [
  "Summarize a care update for a family member.",
  "Help me outline a short story scene.",
  "Turn notes into a calm conversational response.",
];

function formatCost(costUsd: number | null | undefined): string | null {
  if (costUsd == null) return null;
  if (costUsd < 0.001) return `<$0.001`;
  return `$${costUsd.toFixed(4)}`;
}

function MessageBubble({ msg }: { msg: ChatbotMessage }) {
  const isAssistant = msg.role === "assistant";
  const cost = formatCost(msg.cost_usd);

  return (
    <article className={`flex gap-3 ${isAssistant ? "" : "justify-end"}`} data-testid={`message-${msg.role}`}>
      {isAssistant ? (
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-ink-900 text-paper">
          <Bot className="h-5 w-5" />
        </div>
      ) : null}
      <div
        className={`max-w-2xl rounded-[24px] px-5 py-4 text-sm leading-7 ${
          isAssistant ? "bg-[var(--bg-chat-assistant)] text-ink-900" : "bg-ink-900 text-paper"
        }`}
      >
        <p className="mb-2 text-xs uppercase tracking-[0.24em] opacity-70">
          {isAssistant ? "Assistant" : "You"}
        </p>
        <p className="whitespace-pre-wrap">{msg.content}</p>
        {isAssistant && (msg.input_tokens || cost) ? (
          <p className="mt-2 text-xs opacity-50">
            {msg.input_tokens ? `${msg.input_tokens}→${msg.output_tokens ?? 0} tokens` : null}
            {cost ? ` · ${cost}` : null}
            {msg.model_name ? ` · ${msg.model_name}` : null}
          </p>
        ) : null}
      </div>
      {!isAssistant ? (
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-amber-600 text-paper">
          <User2 className="h-5 w-5" />
        </div>
      ) : null}
    </article>
  );
}

function SessionRail({
  sessions,
  activeId,
  onSelect,
  onNew,
  onDelete,
}: {
  sessions: ChatbotSession[];
  activeId: number | null;
  onSelect: (id: number) => void;
  onNew: () => void;
  onDelete: (id: number) => void;
}) {
  return (
    <div className="flex flex-col gap-2" data-testid="session-rail">
      <button
        className="flex items-center gap-2 rounded-[20px] bg-white/15 px-4 py-3 text-left text-sm font-medium text-paper/90 transition hover:bg-white/25"
        data-testid="new-session-button"
        onClick={onNew}
        type="button"
      >
        <MessageSquarePlus className="size-4 shrink-0" />
        New conversation
      </button>
      <div className="mt-2 space-y-1">
        {sessions.map((s) => (
          <div
            className={`group flex items-center gap-2 rounded-2xl px-3 py-2.5 transition ${
              activeId === s.id ? "bg-white/20" : "hover:bg-white/10"
            }`}
            key={s.id}
          >
            <button
              className="min-w-0 flex-1 truncate text-left text-sm text-paper/80"
              data-testid="session-item"
              onClick={() => onSelect(s.id)}
              type="button"
            >
              {s.title}
            </button>
            <button
              className="shrink-0 opacity-0 group-hover:opacity-100 text-paper/50 transition hover:text-red-300"
              data-testid="delete-session-button"
              onClick={(e) => { e.stopPropagation(); onDelete(s.id); }}
              type="button"
            >
              <Trash2 className="size-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

interface ChatbotWorkspaceProps {
  initialSessionId?: number | null;
}

export function ChatbotWorkspace({ initialSessionId }: ChatbotWorkspaceProps = {}) {
  const queryClient = useQueryClient();
  const [activeSessionId, setActiveSessionId] = useState<number | null>(initialSessionId ?? null);
  const [draft, setDraft] = useState("");
  const [sendError, setSendError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { data: sessions = [], isLoading: sessionsLoading } = useQuery({
    queryKey: ["chatbot-sessions"],
    queryFn: fetchChatbotSessions,
  });

  const { data: activeSession, isLoading: sessionLoading } = useQuery({
    queryKey: ["chatbot-session", activeSessionId],
    queryFn: () => fetchChatbotSession(activeSessionId!),
    enabled: activeSessionId != null,
  });

  const { mutate: createSession, isPending: creating } = useMutation({
    mutationFn: (title?: string) => createChatbotSession(title),
    onSuccess: (s) => {
      void queryClient.invalidateQueries({ queryKey: ["chatbot-sessions"] });
      setActiveSessionId(s.id);
    },
  });

  const createSessionAndSend = (message: string) => {
    createSession(undefined, {
      onSuccess: (s) => {
        sendMessage({ id: s.id, msg: message });
      },
    });
  };

  const { mutate: deleteSession } = useMutation({
    mutationFn: (id: number) => deleteChatbotSession(id),
    onSuccess: (_, id) => {
      void queryClient.invalidateQueries({ queryKey: ["chatbot-sessions"] });
      if (activeSessionId === id) setActiveSessionId(null);
    },
  });

  const { mutate: sendMessage, isPending: sending } = useMutation({
    mutationFn: ({ id, msg }: { id: number; msg: string }) => sendChatbotMessage(id, msg),
    onSuccess: () => {
      setSendError(null);
      void queryClient.invalidateQueries({ queryKey: ["chatbot-session", activeSessionId] });
      setDraft("");
    },
    onError: (err) => setSendError(err instanceof Error ? err.message : "Failed to send message."),
  });

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activeSession?.messages]);

  function handleSubmit(text: string) {
    const trimmed = text.trim();
    if (!trimmed || sending) return;
    if (activeSessionId == null) {
      createSessionAndSend(trimmed);
      return;
    }
    sendMessage({ id: activeSessionId, msg: trimmed });
  }

  const messages = activeSession?.messages ?? [];

  return (
    <div className="grid gap-6 xl:grid-cols-[0.72fr_1.28fr]">
      <aside className="rounded-[28px] border border-black/10 bg-[linear-gradient(180deg,rgba(31,59,54,0.96),rgba(35,25,19,0.96))] p-6 text-paper shadow-panel">
        <p className="text-xs uppercase tracking-[0.28em] text-paper/70">Chatbot app</p>
        <h2 className="mt-3 font-display text-4xl">Simple chat-first UI.</h2>
        <p className="mt-4 text-sm leading-7 text-paper/75">
          One conversation rail per session. No storytelling or care-circle assumptions inside this surface.
        </p>

        <div className="mt-6">
          {sessionsLoading ? (
            <div className="flex items-center gap-2 text-sm text-paper/50">
              <Loader2 className="size-4 animate-spin" /> Loading sessions…
            </div>
          ) : (
            <SessionRail
              activeId={activeSessionId}
              onDelete={(id) => deleteSession(id)}
              onNew={() => createSession(undefined)}
              onSelect={(id) => setActiveSessionId(id)}
              sessions={sessions}
            />
          )}
        </div>

        <div className="mt-8 space-y-3">
          {starterPrompts.map((prompt) => (
            <button
              className="w-full rounded-[24px] border border-white/15 bg-white/10 px-4 py-4 text-left text-sm leading-6 transition hover:border-white/30 hover:bg-white/15"
              data-testid="starter-prompt"
              key={prompt}
              onClick={() => {
                if (activeSessionId) {
                  sendMessage({ id: activeSessionId, msg: prompt });
                } else {
                  createSessionAndSend(prompt);
                }
              }}
              type="button"
            >
              <span className="flex items-start gap-3">
                <Sparkles className="mt-1 h-4 w-4 shrink-0" />
                <span>{prompt}</span>
              </span>
            </button>
          ))}
        </div>
      </aside>

      <section className="rounded-[32px] border border-black/10 bg-white/75 p-4 shadow-panel md:p-6">
        <div className="flex items-center justify-between border-b border-black/10 pb-4">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Conversation</p>
            <h2 className="mt-2 font-display text-3xl text-ink-900">
              {activeSession?.title ?? "Focused workspace"}
            </h2>
          </div>
          {activeSessionId ? (
            <div className="rounded-full border border-emerald-900/20 bg-emerald-900/10 px-3 py-2 text-xs uppercase tracking-[0.24em] text-emerald-900">
              Session #{activeSessionId}
            </div>
          ) : (
            <div className="rounded-full border border-black/10 px-3 py-2 text-xs uppercase tracking-[0.24em] text-ink-500">
              No session
            </div>
          )}
        </div>

        <div className="mt-6 max-h-[400px] overflow-y-auto space-y-4 pr-1" data-testid="chatbot-messages" ref={scrollRef}>
          {sessionLoading ? (
            <div className="flex h-24 items-center justify-center">
              <Loader2 className="size-5 animate-spin text-ink-400" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex h-24 flex-col items-center justify-center text-sm text-ink-400" data-testid="empty-session">
              <Bot className="size-8 mb-2 opacity-40" />
              {activeSessionId
                ? "No messages yet. Send something to start."
                : "Select or create a session to begin."}
            </div>
          ) : (
            messages.map((msg) => <MessageBubble key={msg.id} msg={msg} />)
          )}

          {sending ? (
            <div className="flex gap-3" data-testid="assistant-pending">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-ink-900 text-paper">
                <Bot className="h-5 w-5" />
              </div>
              <div className="rounded-[24px] bg-[var(--bg-chat-assistant)] px-5 py-4 text-sm">
                <p className="text-xs uppercase tracking-[0.24em] opacity-70 mb-2">Assistant</p>
                <Loader2 className="size-4 animate-spin text-ink-500" />
              </div>
            </div>
          ) : null}
        </div>

        <form
          className="mt-6 flex flex-col gap-3 border-t border-black/10 pt-5"
          onSubmit={(e) => { e.preventDefault(); handleSubmit(draft); }}
        >
          <label className="text-xs uppercase tracking-[0.24em] text-ink-600" htmlFor="chatbot-prompt">
            Prompt
          </label>
          <textarea
            className="min-h-32 rounded-[24px] border border-black/10 bg-[#fcfaf6] px-5 py-4 text-sm leading-7 text-ink-900 outline-none transition focus:border-amber-600 disabled:opacity-50"
            data-testid="chatbot-input"
            disabled={sending || creating}
            id="chatbot-prompt"
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                handleSubmit(draft);
              }
            }}
            placeholder="Ask for a rewrite, a summary, or the next reply in a conversation."
            value={draft}
          />
          {sendError ? (
            <div className="flex items-center gap-2 text-sm text-red-600" data-testid="send-error">
              <p>{sendError}</p>
              <button
                className="flex items-center gap-1 text-xs underline"
                onClick={() => { setSendError(null); handleSubmit(draft); }}
                type="button"
              >
                <RefreshCw className="size-3" />
                Retry
              </button>
            </div>
          ) : null}
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-ink-600">
              {activeSessionId ? "Cmd/Ctrl+Enter to send." : "Create a session to start chatting."}
            </p>
            <Button className="gap-2" disabled={sending || creating || !draft.trim()} type="submit">
              {sending ? <Loader2 className="h-4 w-4 animate-spin" /> : <CornerDownLeft className="h-4 w-4" />}
              {sending ? "Sending…" : "Send message"}
            </Button>
          </div>
        </form>
      </section>
    </div>
  );
}
