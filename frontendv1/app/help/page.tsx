import { PublicShell } from "@/components/shell/public-shell";
import { PageHeader } from "@/components/shell/page-header";

export default function HelpPage() {
  return (
    <PublicShell>
      <div className="space-y-8">
        <PageHeader
          description="Sprint 3 adds the public information route group on the shared shell so legal and support pages stop being late-stage cleanup work."
          eyebrow="Help"
          title="Help is part of the framework, not an afterthought."
        />
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
          <p className="max-w-3xl text-base leading-8 text-ink-700">
            Use the account, billing, and referrals routes as the main Sprint 3 framework examples. Later sprints can attach deeper help content and task-level guides to this same public route family without revisiting the shell structure.
          </p>
        </section>
      </div>
    </PublicShell>
  );
}
