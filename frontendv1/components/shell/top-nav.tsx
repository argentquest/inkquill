"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { CoinBalanceBadge } from "@/components/shell/coin-balance-badge";
import { ThemeToggle } from "@/components/shell/theme-toggle";
import { UserMenu } from "@/components/shell/user-menu";
import { apps, resolveApp } from "@/lib/apps";

export function TopNav() {
  const pathname = usePathname();
  const activeApp = resolveApp(pathname);
  const primaryLinks = activeApp?.primaryLinks ?? [
    { href: "/", label: "Home" },
    { href: "/app/account", label: "Account" },
    { href: "/app/billing", label: "Billing" },
    { href: "/app/referrals", label: "Referrals" },
    { href: "/help", label: "Help" }
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-black/10 bg-paper/85 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 md:px-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-6">
            <Link className="font-display text-2xl tracking-[0.08em] text-ink-900" href="/">
              Ink & Quill
            </Link>
            {activeApp ? (
              <div className="hidden rounded-full border border-black/10 bg-white/70 px-3 py-2 text-xs uppercase tracking-[0.24em] text-ink-600 md:block">
                {activeApp.name}
              </div>
            ) : null}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <CoinBalanceBadge />
            <ThemeToggle />
            <UserMenu />
          </div>
        </div>

        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <nav className="flex flex-wrap items-center gap-3 text-sm text-ink-700">
            {apps.map((app) => {
              const isActive = activeApp?.id === app.id;

              return (
                <Link
                  className={`rounded-full px-3 py-2 transition hover:bg-black/5 hover:text-ink-900 ${isActive ? "bg-ink-900 text-paper hover:bg-ink-900 hover:text-paper" : ""}`}
                  href={app.getEntryHref()}
                  key={app.id}
                >
                  {app.name}
                </Link>
              );
            })}
          </nav>
          <nav className="flex flex-wrap items-center gap-3 text-sm text-ink-700">
            {primaryLinks.map((link) => (
              <Link
                className="rounded-full px-3 py-2 transition hover:bg-black/5 hover:text-ink-900"
                href={link.href}
                key={link.href}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
}
