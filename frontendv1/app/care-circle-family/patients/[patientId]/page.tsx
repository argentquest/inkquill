import Link from "next/link";

import { FamilyPatientDetailClient } from "@/components/care-circle-family/family-patient-detail-client";
import { PageHeader } from "@/components/shell/page-header";

export default async function CareCircleFamilyPatientDetailPage({
  params
}: {
  params: Promise<{ patientId: string }>;
}) {
  const { patientId } = await params;

  return (
    <div className="space-y-8">
      <PageHeader
        action={
          <Link
            className="inline-flex items-center rounded-full border border-black/10 bg-white px-5 py-3 text-sm font-semibold text-ink-900 transition hover:border-black/20"
            href="/care-circle-family/patients"
          >
            Back to friends
          </Link>
        }
        description="The imported profile model captures family members, delivery schedule, care stage, preferred content, and image-based friend sign-in."
        eyebrow="Friend detail"
        title="Friend profile"
      />
      <FamilyPatientDetailClient key={patientId} patientId={patientId} />
    </div>
  );
}
