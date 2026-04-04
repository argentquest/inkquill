import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";

export default function CareCirclePatientPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="This patient-facing route now imports DailyNewsletter’s calm recipient-entry model: direct sign-in, familiar image choices, and a read-only daily view."
        eyebrow="Care Circle Patient"
        title="Direct-entry patient access stays separate and calm by design."
      />
      <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <p className="text-sm leading-7 text-ink-700">
          This surface is intentionally simplified. The first imported behavior is a picture-based sign-in flow that leads to a gentle
          daily highlights session rather than a management dashboard.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            className="inline-flex items-center rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
            href="/care-circle-patient/login"
          >
            Start picture sign-in
          </Link>
        </div>
      </section>
    </div>
  );
}
