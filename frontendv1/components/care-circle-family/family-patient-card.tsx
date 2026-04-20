import { deleteCareCirclePatient } from "@/lib/api";
import type { CareCirclePatientRecord } from "@/lib/api";

import { PatientAccessStateBadge } from "./patient-access-state-badge";

export function FamilyPatientCard({ patient }: { patient: CareCirclePatientRecord }) {
  const handleDelete = async () => {
    if (!confirm(`Delete patient ${patient.displayName} permanently?\n\nThis action cannot be undone.`)) {
      return;
    }

    const confirmation = prompt(`Type DELETE to confirm permanent deletion of ${patient.displayName}:`);
    if (confirmation?.trim() !== "DELETE") {
      alert("Deletion cancelled. You must type DELETE exactly.");
      return;
    }

    try {
      await deleteCareCirclePatient(patient.id);
      alert(`Patient ${patient.displayName} has been permanently deleted.`);
      window.location.reload();
    } catch {
      alert("Failed to delete patient. Check console.");
    }
  };

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

      {patient.preferences.hobbies.length > 0 || patient.preferences.favoriteActivities.length > 0 ? (
        <div className="mt-5 flex flex-wrap gap-2">
          {[...patient.preferences.hobbies, ...patient.preferences.favoriteActivities].map((tag) => (
            <span key={tag} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-1 text-sm text-ink-700">
              {tag}
            </span>
          ))}
        </div>
      ) : null}

      <div className="mt-6 flex items-center justify-between gap-4">
        <p className="text-sm text-ink-700">
          {patient.preferences.familyMembers.length > 0
            ? `Family circle: ${patient.preferences.familyMembers.join(", ")}`
            : null}
        </p>
        
        <div className="flex gap-3">
          <a
            className="inline-flex items-center rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20"
            href={`/care-circle-family/patients/${patient.id}?edit=1`}
          >
            Edit
          </a>
          <button
            onClick={handleDelete}
            className="inline-flex items-center rounded-full border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 hover:bg-red-100 hover:text-red-800 transition"
          >
            Delete
          </button>
        </div>
      </div>
    </article>
  );
}
