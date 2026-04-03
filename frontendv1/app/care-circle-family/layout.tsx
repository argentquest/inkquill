import { AppShellResolver } from "@/components/platform/app-shell-resolver";
import { PlatformAppGate } from "@/components/platform/platform-app-gate";

export default function CareCircleFamilyLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppShellResolver>
      <PlatformAppGate>{children}</PlatformAppGate>
    </AppShellResolver>
  );
}
