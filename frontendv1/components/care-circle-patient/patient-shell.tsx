export function PatientShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(255,246,223,0.92),transparent_32%),linear-gradient(180deg,#fdfaf4_0%,#f4ecdc_100%)]">
      <main className="mx-auto w-full max-w-7xl px-4 py-6 md:px-8 md:py-10">{children}</main>
    </div>
  );
}
