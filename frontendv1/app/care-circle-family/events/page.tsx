"use client";

import { BellRing, ShieldCheck, Heart } from "lucide-react";
import { PageHeader } from "@/components/shell/page-header";

export default function FamilyEventFeedPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Monitor real-time generative interactions, view notifications, and observe caregiver engagement asynchronously."
        eyebrow="Activity Feed"
        title="Family Event Stream"
      />

      <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <ul className="space-y-6">
          <li className="flex gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
             <ShieldCheck className="size-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-ink-900">Provider Backend Stabilized</p>
              <p className="text-sm text-ink-500">The DailyNewsletter sandbox completed its import migration.</p>
              <p className="mt-1 text-xs text-ink-400">10 mins ago</p>
            </div>
          </li>
          <li className="flex gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
             <Heart className="size-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-ink-900">Patient Session Loaded</p>
              <p className="text-sm text-ink-500">Arthur Bloom accessed their daily highlights safely.</p>
              <p className="mt-1 text-xs text-ink-400">2 hours ago</p>
            </div>
          </li>
          <li className="flex gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-amber-100 text-amber-600">
             <BellRing className="size-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-ink-900">Weather API Timeout</p>
              <p className="text-sm text-ink-500">The weather provider fell back to default static state due to network timeout.</p>
              <p className="mt-1 text-xs text-ink-400">Yesterday</p>
            </div>
          </li>
        </ul>
      </section>
    </div>
  );
}
