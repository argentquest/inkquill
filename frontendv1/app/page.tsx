import Link from "next/link";
import { ArrowRight, PanelsTopLeft, PenTool, Sparkles } from "lucide-react";

import { PublicShell } from "@/components/shell/public-shell";
import { PageHeader } from "@/components/shell/page-header";

const rails = [
  {
    title: "Active workspaces",
    description: "Bring the most important worlds, stories, and drafts forward instead of dropping users into a blank admin wall.",
    icon: PanelsTopLeft
  },
  {
    title: "Creative pacing",
    description: "Build room for long-form writing, recent activity, and momentum cues before dense tables arrive in later sprints.",
    icon: PenTool
  },
  {
    title: "System clarity",
    description: "Maintenance, balance, session, and shell state remain visible without flattening the interface into operations chrome.",
    icon: Sparkles
  }
];

export default function HomePage() {
  return (
    <PublicShell>
      <PageHeader
        action={
          <Link
            className="inline-flex items-center gap-2 rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
            href="/app/account"
          >
            Open App Shell
            <ArrowRight className="h-4 w-4" />
          </Link>
        }
        description="Sprint 1 establishes the public shell, app shell, route tree, theme persistence, session bootstrap, balance loading, maintenance awareness, and baseline global states."
        eyebrow="Frontend V1"
        title="Editorial shell, not a generic dashboard."
      />

      <section className="mt-8 grid gap-4 rounded-[28px] border border-black/10 bg-white/65 p-6 shadow-panel lg:grid-cols-3">
        <Link className="rounded-[24px] border border-black/10 bg-[#fcfaf6] p-5 transition hover:border-black/20 hover:bg-white" href="/storytelling">
          <p className="text-xs uppercase tracking-[0.28em] text-ink-600">App one</p>
          <h2 className="mt-3 font-display text-3xl text-ink-900">Storytelling</h2>
          <p className="mt-3 text-sm leading-7 text-ink-700">Creative authoring and editorial workflow surface.</p>
        </Link>
        <Link className="rounded-[24px] border border-black/10 bg-[#fcfaf6] p-5 transition hover:border-black/20 hover:bg-white" href="/care-circle-family">
          <p className="text-xs uppercase tracking-[0.28em] text-ink-600">App two</p>
          <h2 className="mt-3 font-display text-3xl text-ink-900">Care Circle</h2>
          <p className="mt-3 text-sm leading-7 text-ink-700">Family and patient-safe care coordination surface.</p>
        </Link>
        <Link className="rounded-[24px] border border-black/10 bg-[#fcfaf6] p-5 transition hover:border-black/20 hover:bg-white" href="/chatbot">
          <p className="text-xs uppercase tracking-[0.28em] text-ink-600">App three</p>
          <h2 className="mt-3 font-display text-3xl text-ink-900">Chatbot</h2>
          <p className="mt-3 text-sm leading-7 text-ink-700">A simple chat-first UI to validate the app split before deeper domain work.</p>
        </Link>
      </section>

      <section className="mt-8 grid gap-6 lg:grid-cols-3">
        {rails.map((rail) => (
          <article className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel" key={rail.title}>
            <rail.icon className="h-8 w-8 text-ember" />
            <h2 className="mt-5 font-display text-3xl text-ink-900">{rail.title}</h2>
            <p className="mt-3 text-sm leading-7 text-ink-700">{rail.description}</p>
          </article>
        ))}
      </section>
    </PublicShell>
  );
}
