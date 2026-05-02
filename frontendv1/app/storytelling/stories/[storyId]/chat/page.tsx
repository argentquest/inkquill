"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Loader2, MessageSquarePlus, Send, Trash2, Wifi, WifiOff } from "lucide-react";

import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import {
  fetchStoryChatSessions,
  createStoryChatSession,
  fetchStoryChatSession,
  deleteStoryChatSession,
  fetchWsTicket,
  buildStoryChatWsUrl,
  type StoryChatSessionWithMessages,
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

export default function StoryChatPage() {
  const params = useParams<{ storyId: string }>();
  const storyId = Number(params.storyId);
  const queryClient = useQueryClient();
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [composer, setComposer] = useState("");
  const [messages, setMessages] = useState<StoryChatSessionWithMessages["messages"]>([]);
  const [pendingAssistant, setPendingAssistant] = useState("");
  const [wsStatus, setWsStatus] = useState<"idle" | "connecting" | "open" | "closed" | "error">("idle");
  const wsRef = useRef<WebSocket | null>(null);

  const {
    data: sessions,
    isLoading: sessionsLoading,
    error: sessionsError,
    refetch: refetchSessions,
  } = useQuery({
    queryKey: ["story-chat-sessions", storyId],
    queryFn: () => fetchStoryChatSessions(storyId),
    enabled: !isNaN(storyId),
  });

  const {
    data: sessionDetail,
    isLoading: detailLoading,
    error: detailError,
    refetch: refetchDetail,
  } = useQuery({
    queryKey: ["story-chat-session", storyId, activeSessionId],
    queryFn: () => fetchStoryChatSession(storyId, activeSessionId!),
    enabled: !isNaN(storyId) && activeSessionId !== null,
  });

  useEffect(() => {
    if (sessionDetail?.messages) {
      setMessages(sessionDetail.messages);
    }
  }, [sessionDetail]);

  useEffect(() => {
    if (!activeSessionId || isNaN(storyId)) return;

    let cancelled = false;
    setWsStatus("connecting");

    fetchWsTicket()
      .then((ticket) => {
        if (cancelled) return;
        const url = buildStoryChatWsUrl(storyId, activeSessionId, ticket);
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!cancelled) setWsStatus("open");
        };

        ws.onmessage = (event) => {
          if (cancelled) return;
          try {
            const msg = JSON.parse(event.data) as {
              type: string;
              content?: string;
              message?: string;
              session?: unknown;
            };
            switch (msg.type) {
              case "text_chunk":
                setPendingAssistant((prev) => prev + (msg.content ?? ""));
                break;
              case "response_complete":
                setPendingAssistant("");
                queryClient.invalidateQueries({ queryKey: ["story-chat-session", storyId, activeSessionId] });
                break;
              case "error":
                setWsStatus("error");
                break;
              case "session_info":
                // connected successfully
                break;
            }
          } catch {
            // ignore malformed messages
          }
        };

        ws.onerror = () => {
          if (!cancelled) setWsStatus("error");
        };

        ws.onclose = () => {
          if (!cancelled) setWsStatus("closed");
        };
      })
      .catch(() => {
        if (!cancelled) setWsStatus("error");
      });

    return () => {
      cancelled = true;
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [storyId, activeSessionId, queryClient]);

  const createMutation = useMutation({
    mutationFn: () => createStoryChatSession(storyId, { title: "Chat session" }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["story-chat-sessions", storyId] });
      setActiveSessionId(data.id);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (sessionId: number) => deleteStoryChatSession(storyId, sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["story-chat-sessions", storyId] });
      if (activeSessionId !== null) setActiveSessionId(null);
    },
  });

  function handleSend(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const text = composer.trim();
    if (!text || !wsRef.current || wsStatus !== "open") return;

    wsRef.current.send(
      JSON.stringify({ type: "send_message", content: text })
    );

    // Optimistic user message
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        session_id: activeSessionId!,
        role: "user",
        content: text,
        created_at: new Date().toISOString(),
      },
    ]);
    setComposer("");
  }

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
          <Link href={`/storytelling/stories/${storyId}`}>
            <ArrowLeft className="mr-1 size-4" />
            Story
          </Link>
        </Button>
      </div>

      <PageHeader eyebrow="Story Chat" title="Chat" description="Discuss your story with AI." />

      <div className="flex flex-col gap-4 lg:flex-row">
        {/* Sidebar */}
        <aside className="w-full shrink-0 space-y-3 lg:w-64">
          <Button className="w-full gap-2" onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
            <MessageSquarePlus className="size-4" />
            New session
          </Button>

          <div className="space-y-2">
            {(sessions ?? []).length === 0 ? (
              <p className="text-sm text-ink-500">No sessions yet.</p>
            ) : (
              (sessions ?? []).map((s) => (
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
              <div className="flex items-center justify-between border-b border-black/10 px-4 py-2">
                <span className="text-xs font-medium uppercase tracking-wider text-ink-500">
                  {sessionDetail?.title}
                </span>
                <span className="flex items-center gap-1 text-xs text-ink-500">
                  {wsStatus === "open" ? <Wifi className="size-3 text-green-600" /> : <WifiOff className="size-3 text-amber-600" />}
                  {wsStatus === "open" ? "Live" : wsStatus}
                </span>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto p-4">
                {messages.length === 0 && !pendingAssistant && (
                  <p className="text-center text-sm text-ink-500">No messages yet. Say hello!</p>
                )}
                {messages.map((m) => (
                  <ChatMessageBubble key={m.id} role={m.role} content={m.content} />
                ))}
                {pendingAssistant && (
                  <ChatMessageBubble role="assistant" content={pendingAssistant} />
                )}
              </div>

              <form onSubmit={handleSend} className="flex items-center gap-2 border-t border-black/10 p-3">
                <input
                  className="flex-1 rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none transition focus:border-ink-500 focus:ring-1 focus:ring-ink-500"
                  placeholder="Type a message..."
                  value={composer}
                  onChange={(e) => setComposer(e.target.value)}
                />
                <Button type="submit" size="sm" aria-label="Send message" disabled={wsStatus !== "open" || !composer.trim()}>
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
