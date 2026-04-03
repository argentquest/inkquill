import { PageHeader } from "@/components/shell/page-header";

export default function CareCircleFamilyPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="Care Circle remains a separate application with family and patient surfaces, and now inherits the shared AppBase contract alongside storytelling and chatbot."
        eyebrow="Care Circle"
        title="Family-side care workflows stay isolated from the other apps."
      />
      <section className="rounded-[28px] border border-black/10 bg-white/70 p-6 shadow-panel">
        <p className="text-sm leading-7 text-ink-700">
          This route anchors the future family dashboard, patient management, events, and media work without mixing those assumptions into chatbot or storytelling.
        </p>
      </section>
    </div>
  );
}
