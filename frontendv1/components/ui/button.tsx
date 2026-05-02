import type { ButtonHTMLAttributes } from "react";
import { Slot } from "@radix-ui/react-slot";

import { cn } from "@/lib/utils";

export function Button({
  children,
  className,
  type = "button",
  title,
  tooltip,
  variant = "primary",
  size,
  asChild,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "destructive" | "outline";
  tooltip?: string;
  size?: "sm" | "md" | "lg";
  asChild?: boolean;
}) {
  const variants: Record<string, string> = {
    primary: "bg-ink-900 text-paper hover:bg-ink-700",
    secondary: "border border-black/10 bg-white/80 text-ink-900 hover:bg-white",
    ghost: "text-ink-700 hover:bg-black/5",
    destructive: "bg-red-600 text-white hover:bg-red-700",
    outline: "border border-black/10 bg-white text-ink-900 hover:bg-black/5",
  };

  const sizes: Record<string, string> = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-5 py-3 text-sm",
    lg: "px-6 py-4 text-base",
  };

  const Comp = asChild ? Slot : "button";

  return (
    <Comp
      className={cn(
        "inline-flex items-center justify-center rounded-full font-semibold transition disabled:cursor-not-allowed disabled:opacity-60",
        variants[variant] ?? variants.primary,
        size ? sizes[size] : sizes.md,
        className
      )}
      type={asChild ? undefined : type}
      title={title ?? tooltip ?? props["aria-label"] ?? (typeof children === "string" ? children : undefined)}
      {...props}
    >
      {children}
    </Comp>
  );
}
