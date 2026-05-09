import { redirect } from "next/navigation";

import { AppShellResolver } from "@/components/platform/app-shell-resolver";
import { PlatformAppGate } from "@/components/platform/platform-app-gate";
import { features } from "@/lib/features";

export default function StorytellingLayout({ children }: { children: React.ReactNode }) {
  if (!features.storytelling) redirect("/");
  return (
    <AppShellResolver>
      <PlatformAppGate>{children}</PlatformAppGate>
    </AppShellResolver>
  );
}
