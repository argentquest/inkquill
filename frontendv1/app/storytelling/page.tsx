import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";

export default function StorytellingPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        action={
          <Link
            className="inline-flex items-center rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
            href="/chatbot"
          >
            Open chatbot first
          </Link>
        }
        description="Storytelling now resolves as its own application entry and inherits the shared AppBase contract, even before the story routes are built out."
        eyebrow="Storytelling"
        title="Creative authoring remains a separate app surface."
      />
      <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <p className="text-sm leading-7 text-ink-700">
          This entry route is reserved for the storytelling shell, world routes, and story routes defined in the platform plan.
        </p>
      </section>
    </div>
  );
}
