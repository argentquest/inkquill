import { FamilyPatientsClient } from "@/components/care-circle-family/family-patients-client";
import { PageHeader } from "@/components/shell/page-header";

export default function CareCircleFamilyPatientsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="This route imports the DailyNewsletter recipient-management concept into care-circle family workflows: family-managed patient profiles, personalization, and easy-sign-in setup."
        eyebrow="Care Circle Family"
        title="Patient profiles now behave like managed family-side care records."
      />

      <FamilyPatientsClient />
    </div>
  );
}
