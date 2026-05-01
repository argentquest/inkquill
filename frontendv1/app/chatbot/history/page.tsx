"use client";

import { useQuery } from "@tanstack/react-query";
import { Bot, Clock, MessageSquare, Settings, ChevronRight, Loader2, Trash2 } from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/shell/page-header";
import { fetchChatbotSessions, deleteChatbotSession } from "@/lib/api";
import { useQueryClient } from "@tanstack/react-query";

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

export default function ChatbotHistoryPage() {
  const queryClient = useQueryClient();
  const { data: sessions = [], isLoading } = useQuery({
    queryKey: ["chatbot-sessions"],
    queryFn: fetchChatbotSessions,
  });

  async function handleDelete(sessionId: number) {
    if (!confirm("Delete this session?")) return;
    await deleteChatbotSession(sessionId);
    void queryClient.invalidateQueries({ queryKey: ["chatbot-sessions"] });
  }

  return (
    <div className="space-y-8">
      <PageHeader
        description="View and manage your chatbot conversation history."
        eyebrow="Chatbot"
        title="Conversation History"
      />

      <div className="rounded-[24px] border border-black/10 bg-white/75 p-6 shadow-panel">
        {isLoading ? (
          <div className="flex items-center gap-2 py-12 text-ink-500">
            <Loader2 className="size-5 animate-spin" />
            <span>Loading history...</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="flex flex-col items-center py-12 text-ink-400">
            <Clock className="size-10 mb-3 opacity-40" />
            <p className="text-sm">No conversation history yet.</p>
            <Link className="mt-3 text-amber-700 underline" href="/chatbot">
              Start a new conversation
            </Link>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="grid grid-cols-[1fr_auto_auto] gap-4 px-4 py-3 text-xs uppercase tracking-[0.2em] text-ink-500">
              <span>Conversation</span>
              <span>Updated</span>
              <span></span>
            </div>
            {sessions.map((session) => (
              <div
                className="group grid grid-cols-[1fr_auto_auto] items-center gap-4 rounded-2xl px-4 py-4 transition hover:bg-ink-50"
                key={session.id}
              >
                <Link
                  className="flex items-center gap-3 min-w-0"
                  href={`/chatbot/sessions/${session.id}`}
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ink-900 text-paper">
                    <MessageSquare className="size-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate font-medium text-ink-900">{session.title}</p>
                    <p className="text-xs text-ink-500">Session #{session.id}</p>
                  </div>
                </Link>
                <span className="whitespace-nowrap text-sm text-ink-400">
                  {formatDate(session.updated_at)}
                </span>
                <button
                  className="shrink-0 rounded-full p-2 text-ink-400 opacity-0 transition hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
                  data-testid="history-delete-session"
                  onClick={() => void handleDelete(session.id)}
                  title="Delete session"
                  type="button"
                >
                  <Trash2 className="size-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}