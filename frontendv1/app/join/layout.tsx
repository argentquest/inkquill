import { PublicShell } from "@/components/shell/public-shell";

export default function JoinLayout({ children }: { children: React.ReactNode }) {
  return (
    <PublicShell>
      <div className="mx-auto flex min-h-[70vh] max-w-5xl items-center justify-center py-10">
        <div className="w-full max-w-2xl">{children}</div>
      </div>
    </PublicShell>
  );
}
