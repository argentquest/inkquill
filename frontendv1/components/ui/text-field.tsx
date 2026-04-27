import { InputHTMLAttributes } from "react";

import { InlineValidationMessage } from "@/components/ui/inline-validation-message";
import { Tooltip } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
  tooltip?: string;
  showTooltip?: boolean;
}

export function TextField({
  error,
  hint,
  label,
  tooltip,
  showTooltip = false,
  ...props
}: TextFieldProps) {
  const inputTitle = props.title ?? tooltip ?? hint ?? `${label}. Enter or review this value.`;

  return (
    <label className="block">
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-[0.24em] text-ink-600">{label}</span>
        {showTooltip && tooltip && (
          <Tooltip content={tooltip} position="right" variant="icon" />
        )}
      </div>
      <input
        className={cn(
          "mt-2 w-full rounded-[20px] border bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200",
          error ? "border-[#c65353]/50" : "border-black/10"
        )}
        title={inputTitle}
        {...props}
      />
      {hint ? <p className="mt-2 text-sm text-ink-600">{hint}</p> : null}
      <InlineValidationMessage message={error} />
    </label>
  );
}
