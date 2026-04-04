import Link from "next/link";
import { notFound } from "next/navigation";

import { PatientSessionClient } from "@/components/care-circle-patient/patient-session-client";
import { PageHeader } from "@/components/shell/page-header";

export default async function CareCirclePatientHomePage({
  searchParams
}: {
  searchParams: Promise<{ patient?: string }>;
}) {
  const params = await searchParams;

  if (!params.patient) {
    notFound();
  }

  return (
    <div className="space-y-8">
      <PageHeader
        action={
          <Link
            className="inline-flex items-center rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-ink-900 transition hover:border-black/20"
            href="/care-circle-patient/login"
          >
            Switch patient
          </Link>
        }
        description="Your family prepared a calm daily view with familiar updates and gentle prompts."
        eyebrow="Daily highlights"
        title="Your day is ready."
      />
      <PatientSessionClient patientId={params.patient} />
    </div>
  );
}
