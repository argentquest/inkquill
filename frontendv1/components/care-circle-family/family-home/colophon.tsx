"use client";

export function Colophon({
  familyName,
  patientName,
}: {
  familyName?: string;
  patientName?: string;
}) {
  return (
    <footer className="relative pb-2 pt-6">
      {/* Triple rule */}
      <div className="space-y-0.5">
        <div className="h-px bg-ink-900/15" />
        <div className="h-px bg-ink-900/15" />
        <div className="h-px bg-ink-900/15" />
      </div>

      <p className="mt-4 text-center font-sans text-sm italic text-ink-500">
        The {familyName ?? "Family"} Circle · Caring for{" "}
        {patientName ?? "our loved ones"} · Printed with love
      </p>
    </footer>
  );
}
