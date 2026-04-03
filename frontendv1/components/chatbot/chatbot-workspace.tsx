"use client";

import { FormEvent, useState } from "react";
import { Bot, CornerDownLeft, Sparkles, User2 } from "lucide-react";

import { Button } from "@/components/ui/button";

interface ChatMessage {
  id: number;
  role: "assistant" | "user";
  text: string;
}

const starterPrompts = [
  "Summarize a care update for a family member.",
  "Help me outline a short story scene.",
  "Turn notes into a calm conversational response."
];

const cannedReplies = [
  "I can help with that. Give me the goal, the audience, and the tone you want.",
  "Start with the key point, then add the minimum context needed to keep it clear.",
  "That works well as a short exchange. If you want, I can turn it into a fuller draft next."
];

export function ChatbotWorkspace() {
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: "assistant",
      text: "Chatbot is ready. Type a prompt and the workspace will keep the exchange focused on one clean thread."
    }
  ]);

  function submitMessage(text: string) {
    const nextText = text.trim();
    if (!nextText) {
      return;
    }

    setMessages((current) => [
      ...current,
      { id: current.length + 1, role: "user", text: nextText },
      { id: current.length + 2, role: "assistant", text: cannedReplies[current.length % cannedReplies.length] }
    ]);
    setDraft("");
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitMessage(draft);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.72fr_1.28fr]">
      <aside className="rounded-[28px] border border-black/10 bg-[linear-gradient(180deg,rgba(31,59,54,0.96),rgba(35,25,19,0.96))] p-6 text-paper shadow-panel">
        <p className="text-xs uppercase tracking-[0.28em] text-paper/70">Chatbot app</p>
        <h2 className="mt-3 font-display text-4xl">Simple chat-first UI.</h2>
        <p className="mt-4 text-sm leading-7 text-paper/75">
          This app is intentionally narrow: one conversation rail, a short prompt queue, and no storytelling or care-circle workflow assumptions inside the surface.
        </p>

        <div className="mt-8 space-y-3">
          {starterPrompts.map((prompt) => (
            <button
              className="w-full rounded-[24px] border border-white/15 bg-white/10 px-4 py-4 text-left text-sm leading-6 transition hover:border-white/30 hover:bg-white/15"
              key={prompt}
              onClick={() => submitMessage(prompt)}
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
            <h2 className="mt-2 font-display text-3xl text-ink-900">Focused workspace</h2>
          </div>
          <div className="rounded-full border border-emerald-900/20 bg-emerald-900/10 px-3 py-2 text-xs uppercase tracking-[0.24em] text-emerald-900">
            Local UI prototype
          </div>
        </div>

        <div className="mt-6 space-y-4" data-testid="chatbot-messages">
          {messages.map((message) => {
            const isAssistant = message.role === "assistant";

            return (
              <article className={`flex gap-3 ${isAssistant ? "" : "justify-end"}`} key={message.id}>
                {isAssistant ? (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-ink-900 text-paper">
                    <Bot className="h-5 w-5" />
                  </div>
                ) : null}
                <div
                  className={`max-w-2xl rounded-[24px] px-5 py-4 text-sm leading-7 ${
                    isAssistant
                      ? "bg-[linear-gradient(135deg,rgba(246,241,232,0.96),rgba(220,229,226,0.88))] text-ink-900"
                      : "bg-ink-900 text-paper"
                  }`}
                >
                  <p className="mb-2 text-xs uppercase tracking-[0.24em] opacity-70">
                    {isAssistant ? "Assistant" : "You"}
                  </p>
                  <p>{message.text}</p>
                </div>
                {!isAssistant ? (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-600 text-paper">
                    <User2 className="h-5 w-5" />
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>

        <form className="mt-6 flex flex-col gap-3 border-t border-black/10 pt-5" onSubmit={handleSubmit}>
          <label className="text-xs uppercase tracking-[0.24em] text-ink-600" htmlFor="chatbot-prompt">
            Prompt
          </label>
          <textarea
            className="min-h-32 rounded-[24px] border border-black/10 bg-[#fcfaf6] px-5 py-4 text-sm leading-7 text-ink-900 outline-none transition focus:border-amber-600"
            id="chatbot-prompt"
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ask for a rewrite, a summary, or the next reply in a conversation."
            value={draft}
          />
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-ink-600">Start simple here before adding storytelling and care-circle behaviors.</p>
            <Button className="gap-2" type="submit">
              Send message
              <CornerDownLeft className="h-4 w-4" />
            </Button>
          </div>
        </form>
      </section>
    </div>
  );
}
