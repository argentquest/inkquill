import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Button({
  children,
  className,
  type = "button",
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
}) {
  const variants = {
    primary: "bg-ink-900 text-paper hover:bg-ink-700",
    secondary: "border border-black/10 bg-white/80 text-ink-900 hover:bg-white",
    ghost: "text-ink-700 hover:bg-black/5"
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60",
        variants[variant],
        className
      )}
      type={type}
      {...props}
    >
      {children}
    </button>
  );
}
