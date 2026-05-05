export interface AppNavLink {
  href: string;
  label: string;
  /** When true, TopNav only renders this link for family owners. */
  ownerOnly?: boolean;
  /** When true, TopNav only renders this link for admin users. */
  adminOnly?: boolean;
  /** When set, TopNav only renders this link when the current path starts with one of these prefixes. */
  visibleOnPaths?: string[];
  /** When set, this link is grouped under a named submenu in TopNav. */
  group?: string;
  /** When true, the link is shown in the user menu rather than top nav. */
  menuOnly?: boolean;
}

export interface AppDefinition {
  id: string;
  name: string;
  /** Returns the canonical entry path for this app. */
  getEntryHref: () => string;
  /** Top-level nav links shown while inside this app. */
  primaryLinks: AppNavLink[];
  /** Path prefixes that belong to this app. */
  pathPrefixes: string[];
}

export const apps: AppDefinition[] = [
  {
    id: "storytelling",
    name: "Storytelling",
    getEntryHref: () => "/storytelling",
    pathPrefixes: ["/storytelling", "/app"],
    primaryLinks: [
      { href: "/storytelling/stories", label: "Stories" },
      { href: "/storytelling/worlds", label: "Worlds" },
      { href: "/storytelling/documents", label: "Documents" },
      { href: "/storytelling/community", label: "Community" },
      { href: "/storytelling/published", label: "Published" },
      { href: "/public/blog", label: "Blog" },
      { href: "/community/forums", label: "Forum" },
      { href: "/storytelling/blog", label: "My Blog", adminOnly: true },
      { href: "/storytelling/account", label: "Account", group: "admin" },
      { href: "/storytelling/billing", label: "Billing", group: "admin" },
      { href: "/storytelling/referrals", label: "Referrals", group: "admin" },
      { href: "/help", label: "Help" },
    ],
  },
  {
    id: "care-circle",
    name: "Care Circle",
    getEntryHref: () => "/care-circle-family",
    pathPrefixes: ["/care-circle-family", "/care-circle-patient"],
    primaryLinks: [
      { href: "/care-circle-family", label: "Family Home" },
      { href: "/care-circle-family/patients", label: "Friends" },
      { href: "/care-circle-family/events", label: "Activity" },
      { href: "/care-circle-family/media", label: "Media" },
      { href: "/care-circle-family/blog", label: "Blog", adminOnly: true },
      { href: "/community/forums", label: "Forum" },
      { href: "/care-circle-family/members", label: "Members", group: "admin" },
      { href: "/care-circle-family/account", label: "Account", group: "admin" },
      { href: "/care-circle-family/providers", label: "Providers", group: "admin" },
      { href: "/care-circle-family/admin", label: "Admin Console", ownerOnly: true, group: "admin" },
      { href: "/care-circle-family/billing", label: "Billing", ownerOnly: true, group: "admin" },
      { href: "/care-circle-family/referrals", label: "Referrals", ownerOnly: true, group: "admin" },
      { href: "/help", label: "Help" },
    ],
  },
  {
    id: "chatbot",
    name: "Chatbot",
    getEntryHref: () => "/chatbot",
    pathPrefixes: ["/chatbot"],
    primaryLinks: [
      { href: "/chatbot", label: "Chat" },
      { href: "/chatbot/history", label: "History" },
      { href: "/chatbot/settings", label: "Settings" },
      { href: "/help", label: "Help" },
    ],
  },
];

export const publicNavLinks: AppNavLink[] = [
  { href: "/", label: "Home" },
  { href: "/public/blog", label: "Blog" },
  { href: "/public/search", label: "Search", visibleOnPaths: ["/public/blog", "/community/forums"] },
  { href: "/public/published-stories", label: "Stories", visibleOnPaths: ["/storytelling", "/public/published-stories"] },
  { href: "/help", label: "Help" },
];

/**
 * Returns the matching app for the given pathname, or null for public routes.
 */
export function resolveApp(pathname: string): AppDefinition | null {
  return (
    apps.find((app) =>
      app.pathPrefixes.some(
        (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
      )
    ) ?? null
  );
}

/**
 * Build account-route base for the active app so menus link to the
 * correct app-scoped account surface.
 */
export function getAppAccountBase(pathname: string): string {
  const app = resolveApp(pathname);
  if (!app) return "/app";
  switch (app.id) {
    case "care-circle":
      return "/care-circle-family/account";
    case "chatbot":
      return "/app";
    case "storytelling":
    default:
      return "/storytelling/account";
  }
}
