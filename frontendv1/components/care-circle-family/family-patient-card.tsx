import type { CareCirclePatientRecord } from "@/lib/api";

import { PatientAccessStateBadge } from "./patient-access-state-badge";

export function FamilyPatientCard({ patient }: { patient: CareCirclePatientRecord }) {
  return (
    <article className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-ink-600">{patient.familyName}</p>
          <h2 className="mt-2 font-display text-3xl text-ink-900">{patient.displayName}</h2>
          <p className="mt-3 text-sm leading-7 text-ink-700">
            Stage {patient.stage} care profile with delivery at {patient.deliveryTime ?? "Flexible"} in {patient.timezone}.
          </p>
        </div>
        <PatientAccessStateBadge state={patient.accessState as "active" | "inactive" | "archived"} />
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {patient.preferences.map((preference) => (
          <span key={preference} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-1 text-sm text-ink-700">
            {preference}
          </span>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-between gap-4">
        <p className="text-sm text-ink-700">Family circle: {patient.familyMembers.join(", ")}</p>
        <a
          className="inline-flex items-center rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
          href={`/care-circle-family/patients/${patient.id}`}
        >
          Open patient
        </a>
      </div>
    </article>
  );
}
