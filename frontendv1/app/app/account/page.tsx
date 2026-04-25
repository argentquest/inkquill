import { PlatformRouteBridge } from "@/components/platform/platform-route-bridge";
import { HelpButton } from "@/components/ui/help-modal";
import { accountHelp } from "@/lib/help-content";

export default function LegacyAccountPage() {
  return (
    <>
      <PlatformRouteBridge />
      <HelpButton helpContent={accountHelp} position="bottom-right" />
    </>
  );
}
