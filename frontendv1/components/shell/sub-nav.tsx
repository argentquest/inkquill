"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSession } from "@/components/providers/app-providers";
import { resolveApp } from "@/lib/apps";

export function SubNav() {
  const pathname = usePathname();
  const session = useSession();
  const activeApp = resolveApp(pathname);

  if (!activeApp) return null;

  const isFamilyOwner = session.status === "authenticated" && session.user?.is_family_owner === true;
  const visibleLinks = activeApp.primaryLinks.filter(
    (link) => !link.ownerOnly || isFamilyOwner
  );

  return (
    <nav
      aria-label={`${activeApp.name} sub-navigation`}
      className="-mx-4 overflow-x-auto border-b border-black/5 bg-white/40 px-4 py-2 md:-mx-6 md:px-6"
    >
      <div className="flex items-center gap-1">
        {visibleLinks.map((link) => {
          const isActive = pathname === link.href || pathname.startsWith(`${link.href}/`);
          return (
            <Link
              key={link.href}
              className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-medium transition ${
                isActive
                  ? "bg-ink-900 text-paper"
                  : "text-ink-600 hover:bg-black/5 hover:text-ink-900"
              }`}
              href={link.href}
            >
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
