"use client";

import { useState, useRef, useEffect } from "react";
import { Info } from "lucide-react";

interface TooltipProps {
  content: string;
  children?: React.ReactNode;
  position?: "top" | "bottom" | "left" | "right";
  variant?: "icon" | "text";
  iconSize?: "sm" | "md";
}

/**
 * Tooltip - A reusable tooltip component for field-level help.
 * 
 * @param content - The tooltip text to display
 * @param children - Optional custom trigger element (default: info icon)
 * @param position - Tooltip position relative to trigger (default: "top")
 * @param variant - "icon" shows an info icon, "text" shows a text link
 * @param iconSize - Size of the info icon ("sm" | "md", default: "sm")
 */
export function Tooltip({
  content,
  children,
  position = "top",
  variant = "icon",
  iconSize = "sm"
}: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        tooltipRef.current &&
        triggerRef.current &&
        !tooltipRef.current.contains(event.target as Node) &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        setIsVisible(false);
      }
    }

    if (isVisible) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isVisible]);

  const positionClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2"
  };

  const arrowClasses = {
    top: "top-full left-1/2 -translate-x-1/2 border-t-ink-900 border-x-transparent border-b-transparent",
    bottom: "bottom-full left-1/2 -translate-x-1/2 border-b-ink-900 border-x-transparent border-t-transparent",
    left: "left-full top-1/2 -translate-y-1/2 border-l-ink-900 border-y-transparent border-r-transparent",
    right: "right-full top-1/2 -translate-y-1/2 border-r-ink-900 border-y-transparent border-l-transparent"
  };

  const iconSizes = {
    sm: "size-3.5",
    md: "size-4"
  };

  return (
    <div className="relative inline-flex">
      <div ref={triggerRef}>
        {variant === "icon" ? (
          <button
            type="button"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
            onFocus={() => setIsVisible(true)}
            onBlur={() => setIsVisible(false)}
            className="inline-flex items-center justify-center text-ink-400 transition hover:text-ink-600 focus:outline-none"
            aria-label="More information"
          >
            <Info className={iconSizes[iconSize]} />
          </button>
        ) : children ? (
          <div
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
            onFocus={() => setIsVisible(true)}
            onBlur={() => setIsVisible(false)}
          >
            {children}
          </div>
        ) : (
          <button
            type="button"
            onMouseEnter={() => setIsVisible(true)}
            onMouseLeave={() => setIsVisible(false)}
            onFocus={() => setIsVisible(true)}
            onBlur={() => setIsVisible(false)}
            className="inline-flex items-center gap-1 text-xs text-ink-500 underline decoration-dotted underline-offset-2 transition hover:text-ink-700"
          >
            <Info className={iconSizes[iconSize]} />
            <span>More info</span>
          </button>
        )}
      </div>

      {isVisible && (
        <div
          ref={tooltipRef}
          className={`
            absolute z-50 w-64 rounded-xl border border-black/10 bg-ink-900 p-3 text-sm text-paper shadow-lg
            ${positionClasses[position]}
          `}
          role="tooltip"
        >
          <div
            className={`
              absolute size-0 border-4
              ${arrowClasses[position]}
            `}
          />
          <p className="leading-relaxed">{content}</p>
        </div>
      )}
    </div>
  );
}

/**
 * FieldTooltip - A tooltip designed specifically for form fields.
 * Integrates with form labels and fields.
 */
export function FieldTooltip({
  label,
  tooltip,
  required,
  children
}: {
  label: string;
  tooltip: string;
  required?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <label className="block">
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-[0.24em] text-ink-600">
          {label}
          {required && <span className="ml-1 text-ember">*</span>}
        </span>
        <Tooltip content={tooltip} position="right" variant="icon" />
      </div>
      {children}
    </label>
  );
}
