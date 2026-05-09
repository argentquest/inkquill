"use client";

function formatDate(date: Date): string {
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function FamilyMasthead({
  familyName,
  patientName,
  weather,
  contributorsCount,
  edition,
}: {
  familyName: string;
  patientName: string;
  weather?: string;
  contributorsCount?: number;
  edition?: string;
}) {
  return (
    <header className="relative rounded-[28px] border border-black/10 bg-paper p-8 shadow-panel">
      {/* Top single rule */}
      <div className="absolute left-8 right-8 top-5 h-px bg-ink-900/20" />

      <div className="flex items-start justify-between pt-4">
        <span className="font-display text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
          {edition ?? "The Family Daily"}
        </span>
        <span className="font-display text-xs font-semibold uppercase tracking-[0.18em] text-ink-400">
          {formatDate(new Date())}
        </span>
      </div>

      {/* Masthead title */}
      <h1 className="mt-5 text-center font-display text-4xl font-semibold leading-tight text-ink-900 md:text-5xl">
        The {familyName} Family Circle
      </h1>

      {/* Foot line */}
      <p className="mt-4 text-center font-sans text-sm italic text-ink-600">
        Caring for{" "}
        <strong className="font-semibold not-italic text-ember">
          {patientName}
        </strong>
        {weather && <span> · {weather}</span>}
        {typeof contributorsCount === "number" && (
          <span> · {contributorsCount} contributor{contributorsCount !== 1 ? "s" : ""} today</span>
        )}
      </p>

      {/* Bottom double rule */}
      <div className="absolute bottom-5 left-8 right-8">
        <div className="h-px bg-ink-900/20" />
        <div className="mt-0.5 h-px bg-ink-900/20" />
      </div>
    </header>
  );
}
