import { redirect } from "next/navigation";

import { AppShell } from "@/components/shell/app-shell";
import { AppShellGuard } from "@/components/shell/app-shell-guard";
import { features } from "@/lib/features";

export default function ChatbotLayout({ children }: { children: React.ReactNode }) {
  if (!features.chat) redirect("/");
  return (
    <AppShell>
      <AppShellGuard>{children}</AppShellGuard>
    </AppShell>
  );
}
