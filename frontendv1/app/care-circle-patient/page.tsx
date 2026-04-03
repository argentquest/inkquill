import { PageHeader } from "@/components/shell/page-header";

export default function CareCirclePatientPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="This patient-facing route establishes the separate low-complexity surface the common platform sprint requires."
        eyebrow="Care Circle Patient"
        title="Direct-entry patient access stays separate from family and storytelling."
      />
      <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <p className="text-sm leading-7 text-ink-700">
          This surface is intentionally simplified and can later attach its own sign-in flow, session rules, and patient-safe navigation without inheriting the family dashboard patterns.
        </p>
      </section>
    </div>
  );
}
