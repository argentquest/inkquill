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
    <header className="flex flex-col gap-6 rounded-[32px] border border-black/10 bg-[linear-gradient(135deg,rgba(246,241,232,0.96),rgba(220,229,226,0.9))] p-8 shadow-panel lg:flex-row lg:items-end lg:justify-between">
      <div className="max-w-3xl">
        <p className="text-xs uppercase tracking-[0.32em] text-ink-600">{eyebrow}</p>
        <h1 className="mt-3 font-display text-4xl leading-tight text-ink-900 md:text-5xl">{title}</h1>
        <p className="mt-4 max-w-2xl text-base leading-8 text-ink-700">{description}</p>
      </div>
      {action ? <div>{action}</div> : null}
    </header>
  );
}
