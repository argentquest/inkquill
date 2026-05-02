"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, MessageSquarePlus, Send, Trash2 } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import {
  fetchWorldChatSessions,
  createWorldChatSession,
  fetchWorldChatSession,
  sendWorldChatMessage,
  deleteWorldChatSession,
} from "@/lib/api";

function ChatMessageBubble({
  role,
  content,
}: {
  role: string;
  content: string;
}) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? "rounded-br-sm bg-ink-900 text-white"
            : "rounded-bl-sm border border-black/10 bg-white/80 text-ink-800 shadow-panel"
        }`}
      >
        {content || <span className="italic opacity-60">Thinking…</span>}
      </div>
    </div>
  );
}

export default function WorldChatPage() {
  const params = useParams<{ worldId: string }>();
  const worldId = Number(params.worldId);
  const queryClient = useQueryClient();
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [composer, setComposer] = useState("");

  const {
    data: sessionsData,
    isLoading: sessionsLoading,
    error: sessionsError,
    refetch: refetchSessions,
  } = useQuery({
    queryKey: ["world-chat-sessions", worldId],
    queryFn: () => fetchWorldChatSessions(worldId),
    enabled: !isNaN(worldId),
  });

  const {
    data: sessionDetail,
    isLoading: detailLoading,
    error: detailError,
    refetch: refetchDetail,
  } = useQuery({
    queryKey: ["world-chat-session", worldId, activeSessionId],
    queryFn: () => fetchWorldChatSession(worldId, activeSessionId!),
    enabled: !isNaN(worldId) && activeSessionId !== null,
  });

  const createMutation = useMutation({
    mutationFn: () => createWorldChatSession(worldId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["world-chat-sessions", worldId] });
      setActiveSessionId(data.id);
    },
  });

  const sendMutation = useMutation({
    mutationFn: (message: string) =>
      sendWorldChatMessage(worldId, activeSessionId!, { message }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["world-chat-session", worldId, activeSessionId] });
      setComposer("");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (sessionId: number) => deleteWorldChatSession(worldId, sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["world-chat-sessions", worldId] });
      if (activeSessionId !== null) setActiveSessionId(null);
    },
  });

  const sessions = sessionsData?.sessions ?? [];

  if (sessionsLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="size-6 animate-spin text-ink-500" />
      </div>
    );
  }

  if (sessionsError) {
    return (
      <ErrorState
        detail={sessionsError instanceof Error ? sessionsError.message : "Try refreshing."}
        onRetry={() => void refetchSessions()}
        retryLabel="Reload sessions"
        title="Chat could not be loaded."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link href={`/storytelling/worlds/${worldId}`}>
            <ArrowLeft className="mr-1 size-4" />
            World
          </Link>
        </Button>
      </div>

      <PageHeader eyebrow="World Chat" title="Chat" description="Discuss your world with AI." />

      <div className="flex flex-col gap-4 lg:flex-row">
        {/* Sidebar */}
        <aside className="w-full shrink-0 space-y-3 lg:w-64">
          <Button className="w-full gap-2" onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
            <MessageSquarePlus className="size-4" />
            New session
          </Button>

          <div className="space-y-2">
            {sessions.length === 0 ? (
              <p className="text-sm text-ink-500">No sessions yet.</p>
            ) : (
              sessions.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setActiveSessionId(s.id)}
                  className={`flex w-full items-center justify-between rounded-xl border px-3 py-2 text-left text-sm transition ${
                    activeSessionId === s.id
                      ? "border-ink-500 bg-ink-900 text-white shadow-panel"
                      : "border-black/10 bg-white/70 text-ink-700 hover:bg-white"
                  }`}
                >
                  <span className="truncate">{s.title || `Session ${s.id}`}</span>
                  <Trash2
                    className="size-3.5 shrink-0 opacity-60 hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm("Delete this session?")) deleteMutation.mutate(s.id);
                    }}
                  />
                </button>
              ))
            )}
          </div>
        </aside>

        {/* Main chat area */}
        <section className="flex min-h-[24rem] flex-1 flex-col rounded-2xl border border-black/10 bg-white/70 shadow-panel">
          {!activeSessionId ? (
            <div className="flex flex-1 items-center justify-center p-8 text-center text-sm text-ink-500">
              Select a session to start chatting, or create a new one.
            </div>
          ) : detailLoading ? (
            <div className="flex flex-1 items-center justify-center">
              <Loader2 className="size-6 animate-spin text-ink-500" />
            </div>
          ) : detailError ? (
            <div className="flex flex-1 items-center justify-center p-8">
              <ErrorState
                detail={detailError instanceof Error ? detailError.message : "Try refreshing."}
                onRetry={() => void refetchDetail()}
                retryLabel="Reload messages"
                title="Messages could not be loaded."
              />
            </div>
          ) : (
            <>
              <div className="flex-1 space-y-4 overflow-y-auto p-4">
                {sessionDetail?.messages.length === 0 && (
                  <p className="text-center text-sm text-ink-500">No messages yet. Say hello!</p>
                )}
                {sessionDetail?.messages.map((m) => (
                  <ChatMessageBubble key={m.id} role={m.role} content={m.content} />
                ))}
              </div>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  const text = composer.trim();
                  if (!text || sendMutation.isPending) return;
                  sendMutation.mutate(text);
                }}
                className="flex items-center gap-2 border-t border-black/10 p-3"
              >
                <input
                  className="flex-1 rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none transition focus:border-ink-500 focus:ring-1 focus:ring-ink-500"
                  placeholder="Type a message..."
                  value={composer}
                  onChange={(e) => setComposer(e.target.value)}
                />
                <Button type="submit" size="sm" aria-label="Send message" disabled={sendMutation.isPending || !composer.trim()}>
                  <Send className="size-4" />
                </Button>
              </form>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
