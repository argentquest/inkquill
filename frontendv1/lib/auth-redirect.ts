/**
 * Helpers for safe `next` redirect handling after login / register.
 */

const ALLOWED_PREFIXES = [
  "/storytelling",
  "/care-circle-family",
  "/care-circle-patient",
  "/chatbot",
  "/app",
  "/help",
  "/public",
];

const DEFAULT_DESTINATION = "/storytelling/account";

/**
 * Validates a `next` query param and returns a safe internal path.
 * External URLs and empty / null values fall back to the default destination.
 */
export function normalizeNextPath(next: string | null | undefined): string {
  if (!next) return DEFAULT_DESTINATION;

  // Reject anything that looks external or protocol-relative
  if (next.startsWith("http") || next.startsWith("//") || next.startsWith("\\")) {
    return DEFAULT_DESTINATION;
  }

  // Must start with /
  if (!next.startsWith("/")) return DEFAULT_DESTINATION;

  // Must match an allowed prefix
  const allowed = ALLOWED_PREFIXES.some(
    (prefix) => next === prefix || next.startsWith(`${prefix}/`)
  );

  return allowed ? next : DEFAULT_DESTINATION;
}
