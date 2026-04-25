"use client";

import { FamilyPatientsClient } from "@/components/care-circle-family/family-patients-client";
import { PageHeader } from "@/components/shell/page-header";
import { HelpButton } from "@/components/ui/help-modal";
import { careCirclePatientsHelp } from "@/lib/help-content";

export default function CareCircleFamilyPatientsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="This route imports the DailyNewsletter recipient-management concept into care-circle family workflows: family-managed friend profiles, personalization, and easy-sign-in setup."
        eyebrow="Care Circle Family"
        title="Friend profiles now behave like managed family-side care records."
      />

      <FamilyPatientsClient />

      <HelpButton helpContent={careCirclePatientsHelp} position="bottom-right" />
    </div>
  );
}
