"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { ChevronDown } from "lucide-react";

import { useSession } from "@/components/providers/app-providers";
import { Breadcrumbs } from "@/components/shell/breadcrumbs";
import { CoinBalanceBadge } from "@/components/shell/coin-balance-badge";
import { ThemeToggle } from "@/components/shell/theme-toggle";
import { UserMenu } from "@/components/shell/user-menu";
import { resolveApp, publicNavLinks, type AppNavLink } from "@/lib/apps";

function NibMark({ className }: { className?: string }) {
  return (
    <svg
      width="56"
      height="56"
      viewBox="0 0 44 44"
      fill="none"
      aria-hidden="true"
      className={className}
    >
      {/* Nib body — warm amber gold */}
      <path d="M22 4 L34 30 L22 26 L10 30 Z" fill="#d97706" />
      {/* Highlight facet */}
      <path d="M22 4 L34 30 L22 26 Z" fill="#f59e0b" opacity="0.55" />
      {/* Centre slit */}
      <path d="M22 8 L22 26" stroke="#fff7ed" strokeWidth="1.4" strokeLinecap="round" />
      {/* Nib hole */}
      <circle cx="22" cy="20" r="1.8" fill="#7c2d12" />
      {/* Ember ink drop */}
      <circle cx="22" cy="37" r="3.4" fill="#d86c3d" />
      <circle cx="22" cy="37" r="1.6" fill="#fb923c" opacity="0.6" />
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
        className="flex items-center gap-1 rounded-full px-3 py-1.5 text-base transition-colors hover:bg-black/5 hover:text-ink-900 text-ink-700"
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
              className="block rounded-2xl px-4 py-2.5 text-base text-ink-700 transition-colors hover:bg-black/[0.04] hover:text-ink-900"
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
          <div className="flex items-center gap-3">
            <Link className="flex items-center gap-2.5 text-ink-900" href="/">
              <NibMark className="text-ink-900" />
              <span className="font-display text-[22px] font-medium tracking-[0.08em]">
                Ink &amp; Quill
              </span>
            </Link>
            {activeApp && (
              <>
                <span className="text-ink-300 text-xl select-none">·</span>
                <Link
                  href={activeApp.getEntryHref()}
                  className="font-display text-[22px] font-medium tracking-[0.08em] text-ink-600 transition-colors hover:text-ink-900"
                >
                  {activeApp.name}
                </Link>
              </>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            {isFamilyOwner && <CoinBalanceBadge />}
            <ThemeToggle />
            <UserMenu />
          </div>
        </div>

        <nav className="flex flex-wrap items-center gap-1 text-base text-ink-700">
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

        {pathname !== "/" && (
          <div className="border-t border-black/[0.07] pt-2.5">
            <Breadcrumbs />
          </div>
        )}
      </div>
    </header>
  );
}
