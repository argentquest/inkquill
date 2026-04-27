import { PatientImageLoginPanel } from "@/components/care-circle-patient/patient-image-login-panel";
import { PageHeader } from "@/components/shell/page-header";
import { HelpButton } from "@/components/ui/help-modal";
import { careCirclePatientLoginHelp } from "@/lib/help-content";

export default function CareCirclePatientLoginPage() {
  return (
    <div className="space-y-8">
      <section className="rounded-[32px] border border-black/10 bg-white/78 px-8 py-10 text-center shadow-panel">
        <p className="font-display text-5xl tracking-[0.08em] text-ink-900 md:text-7xl">Ink &amp; Quill</p>
        <p className="mt-4 text-sm uppercase tracking-[0.32em] text-forest">Simple Picture Login</p>
      </section>
      <PageHeader
        description="Choose your pictures to log in to Ink and Quill."
        eyebrow="Ink and Quill Login"
        title="Log in with your pictures."
      />
      <PatientImageLoginPanel />
      <HelpButton helpContent={careCirclePatientLoginHelp} position="bottom-right" />
    </div>
  );
}
