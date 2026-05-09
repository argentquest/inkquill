import Link from "next/link";

export function SectionHeading({
  title,
  meta,
  action,
}: {
  title: string;
  meta?: string;
  action?: { label: string; href: string };
}) {
  return (
    <div className="flex items-baseline justify-between">
      <div className="flex items-baseline gap-2.5">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-ink-600">{title}</h2>
        {meta && <span className="text-xs text-ink-400">{meta}</span>}
      </div>
      {action && (
        <Link href={action.href} className="text-xs text-ember hover:underline">
          {action.label} →
        </Link>
      )}
    </div>
  );
}
