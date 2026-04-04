import { PatientImageLoginPanel } from "@/components/care-circle-patient/patient-image-login-panel";
import { PageHeader } from "@/components/shell/page-header";

export default function CareCirclePatientLoginPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        description="The first imported DailyNewsletter behavior is patient picture sign-in: direct entry, exactly three familiar images, and no family-dashboard complexity."
        eyebrow="Care Circle Patient"
        title="Picture sign-in gives patients a simpler route into their daily content."
      />
      <PatientImageLoginPanel />
    </div>
  );
}
