import { PlatformRouteBridge } from "@/components/platform/platform-route-bridge";
import { HelpButton } from "@/components/ui/help-modal";
import { onboardingHelp } from "@/lib/help-content";

export default function LegacyOnboardingPage() {
  return (
    <>
      <PlatformRouteBridge />
      <HelpButton helpContent={onboardingHelp} position="bottom-right" />
    </>
  );
}
