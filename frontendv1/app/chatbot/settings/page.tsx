"use client";

import { PageHeader } from "@/components/shell/page-header";
import { Settings, Bot, Coins, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function ChatbotSettingsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Configure how your chatbot assistant works and how usage is tracked."
        eyebrow="Chatbot"
        title="Chatbot Settings"
      />

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-[24px] border border-black/10 bg-white/75 p-6 shadow-panel">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-ink-900 text-paper">
              <Bot className="size-5" />
            </div>
            <h3 className="font-display text-xl text-ink-900">Assistant Model</h3>
          </div>
          <p className="text-sm text-ink-600 mb-4">
            The chatbot uses the default AI model configured for your account. Costs are tracked per turn and deducted from your balance.
          </p>
          <div className="rounded-2xl bg-ink-50 p-4 text-sm text-ink-700">
            <strong>Default model:</strong> GPT-4o (OpenAI)
          </div>
        </div>

        <div className="rounded-[24px] border border-black/10 bg-white/75 p-6 shadow-panel">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-600 text-paper">
              <Coins className="size-5" />
            </div>
            <h3 className="font-display text-xl text-ink-900">Usage & Billing</h3>
          </div>
          <p className="text-sm text-ink-600 mb-4">
            Each conversation turn shows input/output token counts and the estimated cost in USD. View your balance on the billing page.
          </p>
          <Link
            className="inline-flex items-center gap-1 text-sm text-amber-700 hover:underline"
            href="/app/billing"
          >
            View billing <ChevronRight className="size-4" />
          </Link>
        </div>
      </div>

      <div className="rounded-[24px] border border-black/10 bg-white/75 p-6 shadow-panel">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[var(--bg-chat-assistant)] text-ink-900">
            <Settings className="size-5" />
          </div>
          <h3 className="font-display text-xl text-ink-900">Privacy</h3>
        </div>
        <p className="text-sm text-ink-600">
          Chatbot conversations are independent from storytelling and Care Circle data. Sessions are stored securely and can be deleted at any time from the history page.
        </p>
      </div>
    </div>
  );
}