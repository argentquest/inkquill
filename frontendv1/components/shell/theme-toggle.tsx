"use client";

import { MoonStar, SunMedium } from "lucide-react";

import { useTheme } from "@/components/providers/app-providers";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/80 px-4 py-2 text-sm text-ink-800 transition hover:border-black/20 hover:bg-white"
      onClick={toggleTheme}
      title={theme === "light" ? "Night Mode" : "Day Mode"}
      type="button"
    >
      {theme === "light" ? <MoonStar className="h-4 w-4" /> : <SunMedium className="h-4 w-4" />}
      <span>{theme === "light" ? "Night Mode" : "Day Mode"}</span>
    </button>
  );
}
