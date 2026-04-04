import { PatientShell } from "@/components/care-circle-patient/patient-shell";
import { PlatformAppGate } from "@/components/platform/platform-app-gate";

export default function CareCirclePatientLayout({ children }: { children: React.ReactNode }) {
  return (
    <PlatformAppGate>
      <PatientShell>{children}</PatientShell>
    </PlatformAppGate>
  );
}
