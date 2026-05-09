"use client";

const ICONS: Record<string, React.ReactNode> = {
  family: (
    <path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 10c0 5.5-7 10-7 10z" />
  ),
  curated: (
    <>
      <path d="M3 5h7a2 2 0 0 1 2 2v13" />
      <path d="M21 5h-7a2 2 0 0 0-2 2v13" />
      <path d="M3 5v14h18V5" />
    </>
  ),
  auto: (
    <>
      <path d="M12 4v2M12 18v2M4 12h2M18 12h2" />
      <circle cx="12" cy="12" r="3" />
    </>
  ),
};

export function ProvBadge({
  kind = "auto",
  children,
}: {
  kind?: "family" | "curated" | "auto";
  children: React.ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider ${
        kind === "family"
          ? "bg-ember/10 text-ember"
          : kind === "curated"
            ? "bg-forest/10 text-forest"
            : "bg-ink-100 text-ink-600"
      }`}
    >
      <svg
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
      >
        {ICONS[kind]}
      </svg>
      {children}
    </span>
  );
}
