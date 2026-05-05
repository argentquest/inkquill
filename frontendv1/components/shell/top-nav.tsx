"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { CoinBalanceBadge } from "@/components/shell/coin-balance-badge";
import { ThemeToggle } from "@/components/shell/theme-toggle";
import { UserMenu } from "@/components/shell/user-menu";
import { resolveApp, publicNavLinks, type AppNavLink } from "@/lib/apps";

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

function AdminDropdown({ links }: { links: AppNavLink[] }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        aria-expanded={open}
        aria-haspopup="true"
        className="flex items-center gap-1 rounded-full px-3 py-1.5 text-sm transition-colors hover:bg-black/5 hover:text-ink-900 text-ink-700"
        onClick={() => setOpen((v) => !v)}
        type="button"
      >
        Admin
        <ChevronDown className={`size-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>

      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 min-w-[180px] rounded-2xl border border-black/10 bg-paper shadow-lg">
          {links.map((link) => (
            <Link
              key={link.href}
              className="block rounded-2xl px-4 py-2.5 text-sm text-ink-700 transition-colors hover:bg-black/[0.04] hover:text-ink-900"
              href={link.href}
              onClick={() => setOpen(false)}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function TopNav() {
  const pathname = usePathname();
  const session = useSession();
  const activeApp = resolveApp(pathname);
  const primaryLinks = activeApp?.primaryLinks ?? publicNavLinks;

  const isAdmin = session.status === "authenticated" && session.user?.is_admin === true;
  const isFamilyOwner = session.status === "authenticated" && session.user?.is_family_owner === true;

  const visibleLinks = primaryLinks.filter((link) =>
    (!link.ownerOnly || isFamilyOwner) &&
    (!link.adminOnly || isAdmin) &&
    (!link.visibleOnPaths || link.visibleOnPaths.some((p) => pathname === p || pathname.startsWith(`${p}/`)))
  );

  const topLinks = visibleLinks.filter((link) => !link.group);
  const adminGroupLinks = visibleLinks.filter((link) => link.group === "admin");

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
          {topLinks.map((link) => (
            <Link
              className="rounded-full px-3 py-1.5 transition-colors hover:bg-black/5 hover:text-ink-900"
              href={link.href}
              key={link.href}
            >
              {link.label}
            </Link>
          ))}
          {adminGroupLinks.length > 0 && <AdminDropdown links={adminGroupLinks} />}
        </nav>
      </div>
    </header>
  );
}
