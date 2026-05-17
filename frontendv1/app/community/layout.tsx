import { PublicShell } from "@/components/shell/public-shell";

export const dynamic = "force-dynamic";

export default function CommunityLayout({ children }: { children: React.ReactNode }) {
  return <PublicShell>{children}</PublicShell>;
}
