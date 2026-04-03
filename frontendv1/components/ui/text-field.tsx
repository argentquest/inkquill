import { InputHTMLAttributes } from "react";

import { InlineValidationMessage } from "@/components/ui/inline-validation-message";
import { cn } from "@/lib/utils";

export function TextField({
  error,
  hint,
  label,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
  hint?: string;
}) {
  return (
    <label className="block">
      <span className="text-xs uppercase tracking-[0.24em] text-ink-600">{label}</span>
      <input
        className={cn(
          "mt-2 w-full rounded-[20px] border bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200",
          error ? "border-[#c65353]/50" : "border-black/10"
        )}
        {...props}
      />
      {hint ? <p className="mt-2 text-sm text-ink-600">{hint}</p> : null}
      <InlineValidationMessage message={error} />
    </label>
  );
}
