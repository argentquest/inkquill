export function PageHeader({
  eyebrow,
  title,
  description,
  action
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <header className="relative flex flex-col gap-6 overflow-hidden rounded-[28px] border border-black/10 p-8 shadow-panel lg:flex-row lg:items-end lg:justify-between"
      style={{
        background: [
          "radial-gradient(circle at 10% -10%, rgba(220,229,226,0.95), transparent 45%)",
          "radial-gradient(circle at 100% 120%, rgba(216,108,61,0.22), transparent 42%)",
          "linear-gradient(135deg, #f6f1e8 0%, #efe7db 100%)"
        ].join(", ")
      }}
    >
      {/* Forest → Ember accent bar on the leading edge */}
      <div
        aria-hidden="true"
        className="absolute bottom-[14%] left-0 top-[14%] w-1 rounded-full"
        style={{ background: "linear-gradient(180deg, #1f3b36 0%, #d86c3d 100%)" }}
      />

      <div className="max-w-3xl">
        {/* Eyebrow with ember dot */}
        <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-[0.28em] text-forest">
          <span
            aria-hidden="true"
            className="inline-block h-1.5 w-1.5 rounded-full bg-ember"
          />
          {eyebrow}
        </p>
        <h1 className="mt-3 font-display text-4xl font-medium leading-tight text-ink-900 md:text-5xl">
          {title}
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-8 text-ink-700">{description}</p>
      </div>

      {action ? <div className="shrink-0">{action}</div> : null}
    </header>
  );
}
