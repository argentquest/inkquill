import { AppShell } from "@/components/shell/app-shell";
import { AppShellGuard } from "@/components/shell/app-shell-guard";

export default function ChatbotSettingsLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppShell>
      <AppShellGuard>{children}</AppShellGuard>
    </AppShell>
  );
}