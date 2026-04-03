import { cn } from "@/lib/utils";

export function LoadingState({ className, label = "Loading" }: { className?: string; label?: string }) {
  return (
    <div
      className={cn(
        "flex min-h-[180px] items-center justify-center rounded-[28px] border border-black/10 bg-white/70 p-8 text-center shadow-panel",
        className
      )}
    >
      <div>
        <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-ink-200 border-t-ink-700" />
        <p className="mt-4 text-sm uppercase tracking-[0.28em] text-ink-700">{label}</p>
      </div>
    </div>
  );
}
