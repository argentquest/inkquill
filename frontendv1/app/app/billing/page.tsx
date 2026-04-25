import { PlatformRouteBridge } from "@/components/platform/platform-route-bridge";
import { HelpButton } from "@/components/ui/help-modal";
import { billingHelp } from "@/lib/help-content";

export default function LegacyBillingPage() {
  return (
    <>
      <PlatformRouteBridge />
      <HelpButton helpContent={billingHelp} position="bottom-right" />
    </>
  );
}
