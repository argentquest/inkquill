import { PublicShell } from "@/components/shell/public-shell";
import { PageHeader } from "@/components/shell/page-header";

export default function PrivacyPage() {
  return (
    <PublicShell>
      <div className="space-y-8">
        <PageHeader
          description="Privacy and other legal routes now share the same public shell and information architecture as help and about."
          eyebrow="Privacy"
          title="Privacy terms can live inside the new route system from the start."
        />
        <section className="rounded-[28px] border border-black/10 bg-white/80 p-8 shadow-panel">
          <p className="max-w-3xl text-base leading-8 text-ink-700">
            The full legal copy can be swapped in later. For Sprint 3, the key delivery is the route family, shell consistency, and a stable place for backend-agnostic content pages.
          </p>
        </section>
      </div>
    </PublicShell>
  );
}
