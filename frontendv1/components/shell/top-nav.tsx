"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSession } from "@/components/providers/app-providers";
import { CoinBalanceBadge } from "@/components/shell/coin-balance-badge";
import { ThemeToggle } from "@/components/shell/theme-toggle";
import { UserMenu } from "@/components/shell/user-menu";
import { resolveApp } from "@/lib/apps";

function NibMark({ className }: { className?: string }) {
  return (
    <svg
      width="28"
      height="28"
      viewBox="0 0 44 44"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      <path d="M22 4 L34 30 L22 26 L10 30 Z" fill="currentColor" />
      <path d="M22 8 L22 26" stroke="#f6f1e8" strokeWidth="1.2" strokeLinecap="round" />
      <circle cx="22" cy="20" r="1.6" fill="#f6f1e8" />
      <circle cx="22" cy="36" r="3" fill="#d86c3d" />
    </svg>
  );
}

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
    <header className="sticky top-0 z-40 border-b border-black/10 bg-paper/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 md:px-6">
        <div className="flex items-center justify-between">
          <Link className="flex items-center gap-2.5 text-ink-900" href="/">
            <NibMark className="text-ink-900" />
            <span className="font-display text-[22px] font-medium tracking-[0.08em]">
              Ink &amp; Quill
            </span>
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            {isFamilyOwner && <CoinBalanceBadge />}
            <ThemeToggle />
            <UserMenu />
          </div>
        </div>

        <nav className="flex flex-wrap items-center gap-1 text-sm text-ink-700">
          {primaryLinks.filter((link) => !link.ownerOnly || isFamilyOwner).map((link) => (
            <Link
              className="rounded-full px-3 py-1.5 transition-colors hover:bg-black/5 hover:text-ink-900"
              href={link.href}
              key={link.href}
            >
              {link.label}
            </Link>
          ))}
          {isAdmin && (
            <Link
              className="rounded-full px-3 py-1.5 text-ink-500 transition-colors hover:bg-black/5 hover:text-ink-900"
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
