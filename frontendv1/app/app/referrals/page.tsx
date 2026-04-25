import { PlatformRouteBridge } from "@/components/platform/platform-route-bridge";
import { HelpButton } from "@/components/ui/help-modal";
import { referralsHelp } from "@/lib/help-content";

export default function LegacyReferralsPage() {
  return (
    <>
      <PlatformRouteBridge />
      <HelpButton helpContent={referralsHelp} position="bottom-right" />
    </>
  );
}
