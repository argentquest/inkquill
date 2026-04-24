"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSession } from "@/components/providers/app-providers";
import { CoinBalanceBadge } from "@/components/shell/coin-balance-badge";
import { ThemeToggle } from "@/components/shell/theme-toggle";
import { UserMenu } from "@/components/shell/user-menu";
import { resolveApp } from "@/lib/apps";

export function TopNav() {
  const pathname = usePathname();
  const session = useSession();
  const activeApp = resolveApp(pathname);
  const primaryLinks = activeApp?.primaryLinks ?? [
    { href: "/", label: "Home" },
    { href: "/app/account", label: "Account" },
    { href: "/app/billing", label: "Billing" },
    { href: "/app/referrals", label: "Referrals" },
    { href: "/help", label: "Help" }
  ];

  const isAdmin = session.status === "authenticated" && session.user?.is_admin === true;
  const isFamilyOwner = session.status === "authenticated" && session.user?.is_family_owner === true;

  return (
    <header className="sticky top-0 z-40 border-b border-black/10 bg-paper/85 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 md:px-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-6">
            <Link className="font-display text-2xl tracking-[0.08em] text-ink-900" href="/">
              Ink & Quill
            </Link>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {isFamilyOwner && <CoinBalanceBadge />}
            <ThemeToggle />
            <UserMenu />
          </div>
        </div>

        <nav className="flex flex-wrap items-center gap-3 text-sm text-ink-700">
          {primaryLinks.filter((link) => !link.ownerOnly || isFamilyOwner).map((link) => (
            <Link
              className="rounded-full px-3 py-2 transition hover:bg-black/5 hover:text-ink-900"
              href={link.href}
              key={link.href}
            >
              {link.label}
            </Link>
          ))}
          {isAdmin && (
            <Link
              className="rounded-full px-3 py-2 text-ink-500 transition hover:bg-black/5 hover:text-ink-900"
              href="/admin"
            >
              Admin
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
