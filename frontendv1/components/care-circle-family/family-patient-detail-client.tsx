"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { PatientAccessStateBadge } from "@/components/care-circle-family/patient-access-state-badge";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { fetchCareCirclePatient } from "@/lib/api";

export function FamilyPatientDetailClient({ patientId }: { patientId: string }) {
  const { data: patient, isLoading, isError, error } = useQuery({
    queryKey: ["care-circle-family-patient", patientId],
    queryFn: () => fetchCareCirclePatient(patientId),
  });

  if (isLoading) {
    return <LoadingState label="Loading patient profile" />;
  }

  if (isError || !patient) {
    return <ErrorState detail={error instanceof Error ? error.message : "Could not load the patient profile."} title="Patient profile unavailable" />;
  }

  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
        <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <div className="flex items-center justify-between gap-4">
            <h2 className="font-display text-3xl text-ink-900">Profile summary</h2>
            <PatientAccessStateBadge state={patient.accessState as "active" | "inactive" | "archived"} />
          </div>
          <dl className="mt-6 grid gap-5 md:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Family</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.familyName}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Stage</dt>
              <dd className="mt-2 text-base capitalize text-ink-900">{patient.stage}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Delivery</dt>
              <dd className="mt-2 text-base text-ink-900">
                {patient.deliveryTime ?? "Flexible"} · {patient.days.join(", ")}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-[0.24em] text-ink-600">Timezone</dt>
              <dd className="mt-2 text-base text-ink-900">{patient.timezone}</dd>
            </div>
          </dl>
        </article>

        <article className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
          <h2 className="font-display text-3xl text-ink-900">Image sign-in</h2>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            Exactly three familiar images are assigned for direct patient access.
          </p>
          <div className="mt-5 flex flex-wrap gap-2">
            {patient.authImageKeys.map((key) => (
              <span key={key} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm font-semibold capitalize text-ink-900">
                {key}
              </span>
            ))}
          </div>
          <Link className="mt-6 inline-flex rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink-900 transition hover:border-black/20" href="/care-circle-patient/login">
            Preview patient sign-in
          </Link>
        </article>
      </section>

      <section className="rounded-[28px] border border-black/10 bg-white/82 p-6 shadow-panel">
        <h2 className="font-display text-3xl text-ink-900">Patient preferences</h2>
        <div className="mt-5 flex flex-wrap gap-2">
          {patient.preferences.map((preference) => (
            <span key={preference} className="rounded-full border border-black/10 bg-[#fcfaf6] px-3 py-2 text-sm text-ink-700">
              {preference}
            </span>
          ))}
        </div>
        <p className="mt-6 text-sm leading-7 text-ink-700">Family circle: {patient.familyMembers.join(", ")}.</p>
      </section>
    </div>
  );
}
