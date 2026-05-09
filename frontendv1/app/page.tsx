import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { PublicShell } from "@/components/shell/public-shell";
import { PageHeader } from "@/components/shell/page-header";
import { features } from "@/lib/features";

const ALL_APPS = [
  {
    featureKey: "storytelling" as const,
    href: "/storytelling",
    eyebrow: "App one",
    title: "Storytelling",
    description:
      "A full creative-authoring surface for long-form fiction, world-building, and editorial workflow.",
    capabilities: ["User-owned", "AI-assisted writing", "Publishing & community"],
  },
  {
    featureKey: "careCircle" as const,
    href: "/care-circle-family",
    eyebrow: "App two",
    title: "Care Circle",
    description:
      "Family-side coordination, events, friends, and household-owned billing live here.",
    capabilities: ["Family scope", "Realtime ready"],
  },
  {
    featureKey: "chat" as const,
    href: "/chatbot",
    eyebrow: "App three",
    title: "Chat",
    description:
      "A standalone AI chat surface — no world or story context required.",
    capabilities: ["Conversational AI", "Session history"],
  },
];

export default function HomePage() {
  const visibleApps = ALL_APPS.filter((app) => features[app.featureKey]);

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
        description="Choose an application below to get started."
        eyebrow="Ink &amp; Quill"
        title="Your creative and care platform."
      />

      {visibleApps.length > 0 ? (
        <section className="mt-8 grid gap-4 rounded-[28px] border border-black/10 bg-white/65 p-6 shadow-panel lg:grid-cols-2">
          {visibleApps.map((app) => (
            <Link
              key={app.href}
              className="rounded-[24px] border border-black/10 bg-[#fcfaf6] p-6 transition hover:border-black/20 hover:bg-white"
              href={app.href}
            >
              <p className="text-xs uppercase tracking-[0.28em] text-ink-600">{app.eyebrow}</p>
              <h2 className="mt-3 font-display text-3xl text-ink-900">{app.title}</h2>
              <p className="mt-3 text-sm leading-7 text-ink-700">{app.description}</p>
              <ul className="mt-4 flex flex-wrap gap-2">
                {app.capabilities.map((cap) => (
                  <li
                    key={cap}
                    className="rounded-full border border-black/10 bg-white px-3 py-1 text-xs font-medium text-ink-700"
                  >
                    {cap}
                  </li>
                ))}
              </ul>
            </Link>
          ))}
        </section>
      ) : null}
    </PublicShell>
  );
}
