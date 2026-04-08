import type { CareCirclePatientRecord } from "@/lib/api";

const kindLabels: Record<string, string> = {
  family: "Family",
  memory: "Memory",
  activity: "Activity",
  comfort: "Comfort"
};

export function PatientDailyHighlights({ patient }: { patient: CareCirclePatientRecord }) {
  const highlights = patient.highlights ?? [];

  return (
    <section className="space-y-4">
      {highlights.map((highlight) => (
        <article key={`${highlight.providerKey}-${highlight.displayOrder}`} className="rounded-[32px] border border-black/10 bg-white/88 p-6 shadow-panel md:p-8">
          <p className="text-xs uppercase tracking-[0.24em] text-ink-600">{kindLabels[highlight.kind] ?? highlight.kind}</p>
          <h2 className="mt-3 font-display text-3xl text-ink-900 md:text-4xl">{highlight.title}</h2>
          {highlight.renderedHtml ? (
            <div
              className="care-circle-rendered-html mt-4 text-lg leading-8 text-ink-700 md:text-xl"
              dangerouslySetInnerHTML={{ __html: highlight.renderedHtml }}
            />
          ) : (
            <p className="mt-4 text-lg leading-8 text-ink-700 md:text-xl">{highlight.body}</p>
          )}
        </article>
      ))}
    </section>
  );
}
