"use client";

import { InputHTMLAttributes, useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { InlineValidationMessage } from "@/components/ui/inline-validation-message";
import { cn } from "@/lib/utils";

export function PasswordField({
  error,
  hint,
  label,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  error?: string;
  hint?: string;
}) {
  const [visible, setVisible] = useState(false);

  return (
    <label className="block">
      <span className="text-xs uppercase tracking-[0.24em] text-ink-600">{label}</span>
      <div className="relative mt-2">
        <input
          className={cn(
            "w-full rounded-[20px] border bg-white/85 px-4 py-3 pr-14 text-sm text-ink-900 outline-none transition placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200",
            error ? "border-[#c65353]/50" : "border-black/10"
          )}
          type={visible ? "text" : "password"}
          {...props}
        />
        <Button
          aria-label={visible ? "Hide password" : "Show password"}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-2"
          onClick={() => setVisible((current) => !current)}
          type="button"
          variant="ghost"
        >
          {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </Button>
      </div>
      {hint ? <p className="mt-2 text-sm text-ink-600">{hint}</p> : null}
      <InlineValidationMessage message={error} />
    </label>
  );
}
