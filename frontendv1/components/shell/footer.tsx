import Link from "next/link";

const footerLinks = [
  { href: "/public", label: "Public Surfaces" },
  { href: "/app/account", label: "Account" },
  { href: "/", label: "Home" }
];

export function Footer() {
  return (
    <footer className="mt-12 border-t border-black/10 pt-6 text-sm text-ink-700">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <p>Ink & Quill frontend Sprint 1 foundation for the React rebuild.</p>
        <nav className="flex flex-wrap items-center gap-4">
          {footerLinks.map((link) => (
            <Link className="transition hover:text-ink-900" href={link.href} key={link.href}>
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  );
}
