"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

function prettify(segment: string) {
  return segment
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

export function Breadcrumbs() {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);

  return (
    <nav aria-label="Breadcrumb" className="text-sm uppercase tracking-[0.2em] text-ink-500">
      <ol className="flex flex-wrap items-center gap-2">
        <li>
          <Link className="transition hover:text-ink-900" href="/">
            Home
          </Link>
        </li>
        {segments.map((segment, index) => {
          const href = `/${segments.slice(0, index + 1).join("/")}`;
          const isLast = index === segments.length - 1;
          const isMissingIntermediateRoute = href === "/auth";

          return (
            <li className="flex items-center gap-2" key={href}>
              <span>/</span>
              {isLast || isMissingIntermediateRoute ? (
                <span className="text-ink-900">{prettify(segment)}</span>
              ) : (
                <Link className="transition hover:text-ink-900" href={href}>
                  {prettify(segment)}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
