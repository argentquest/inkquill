import Link from "next/link";

import { PageHeader } from "@/components/shell/page-header";

export default function CareCircleFamilyPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Care Circle remains a separate application with family and patient surfaces, and now imports DailyNewsletter-style family-managed patient profiles, provider catalog structure, and picture-based patient access."
        eyebrow="Care Circle"
        title="Family-side care workflows now sit on imported patient and provider foundations."
      />

      <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <p className="text-sm leading-7 text-ink-700">
          This dashboard now anchors the imported family-side model: patient records, provider-driven daily content, and direct-entry
          patient access without mixing those assumptions into chatbot or storytelling.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            className="inline-flex items-center rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
            href="/care-circle-family/patients"
          >
            Open patient profiles
          </Link>
          <Link
            className="inline-flex items-center rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-ink-900 transition hover:border-black/20"
            href="/care-circle-patient/login"
          >
            Preview patient sign-in
          </Link>
        </div>
      </section>
    </div>
  );
}
