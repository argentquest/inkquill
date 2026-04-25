import { PatientImageLoginPanel } from "@/components/care-circle-patient/patient-image-login-panel";
import { PageHeader } from "@/components/shell/page-header";
import { HelpButton } from "@/components/ui/help-modal";
import { careCirclePatientLoginHelp } from "@/lib/help-content";

export default function CareCirclePatientLoginPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="The first imported DailyNewsletter behavior is friend picture sign-in: direct entry, exactly three familiar images, and no family-dashboard complexity."
        eyebrow="Care Circle Friend"
        title="Picture sign-in gives friends a simpler route into their daily content."
      />
      <PatientImageLoginPanel />
      <HelpButton helpContent={careCirclePatientLoginHelp} position="bottom-right" />
    </div>
  );
}
