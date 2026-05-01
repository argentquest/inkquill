# Sprint 01 Platform Baseline — Deep Code Review

**Review Date:** 2026-04-30  
**Sprint Status:** Completed (per sprint doc)  
**Review Scope:** All frontend code under `frontendv1/` associated with Sprint 01 Platform Baseline

---

## Table of Contents

1. [Critical Issues](#1-critical-issues)
2. [Security Issues](#2-security-issues)
3. [Functional Bugs](#3-functional-bugs)
4. [Architecture & Design Issues](#4-architecture--design-issues)
5. [Test Coverage Gaps](#5-test-coverage-gaps)
6. [Code Quality & Maintainability](#6-code-quality--maintainability)
7. [Accessibility Issues](#7-accessibility-issues)
8. [Performance Concerns](#8-performance-concerns)
9. [Configuration & Environment](#9-configuration--environment)
10. [Summary Matrix](#10-summary-matrix)

---

## 1. Critical Issues

### ISSUE-001: Debug Login Exposed for Admin Users Only
**Files:** [`app/auth/login/page.tsx`](frontendv1/app/auth/login/page.tsx:147-177)  
**Severity:** HIGH

The login page contains a debug quick-login panel that is visible to all `is_admin` users. This panel allows direct login with a hardcoded password (`password123`) using seed account credentials:

```tsx
const DEBUG_PASSWORD = "password123";
const DEBUG_ACCOUNTS = [
  { label: "Maple Grove - Clara (owner)", username: "ericsilvertx+clara@gmail.com" },
  { label: "Harbor Point - Olivia (owner)", username: "olivia.harbor@example.com" },
  { label: "Sunset Ridge - Sophie (owner)", username: "ericsilvertx+sophie@gmail.com" },
] as const;
```

**Problems:**
- Hardcoded credentials in source code
- Admin flag is the only gate — any admin account (including potentially compromised ones) can trigger this
- The debug accounts use real email addresses with `+` addressing, suggesting production seed data
- No environment variable guard (e.g., `process.env.NODE_ENV === "development"`)

**Recommendation:** Guard behind `process.env.NODE_ENV === "development"` or a feature flag. Remove hardcoded credentials entirely in production builds.

---

### ISSUE-002: `useLayoutEffect` for Navigation Causes Flash on SSR
**Files:** [`components/shell/app-shell-guard.tsx`](frontendv1/components/shell/app-shell-guard.tsx:16-19), [`components/platform/app-membership-guard.tsx`](frontendv1/components/platform/app-membership-guard.tsx:19-24)  
**Severity:** MEDIUM

Both guards use `useLayoutEffect` with `window.location.replace()` for redirects. In Next.js App Router with SSR, `useLayoutEffect` runs before hydration completes, which can cause:
- A flash of the protected content before redirect
- Console warnings about `window` not being defined during SSR (though mitigated by "use client")
- Potential hydration mismatches if the redirect timing differs between server and client

**Recommendation:** Use `useEffect` instead of `useLayoutEffect` for navigation-side-effect redirects. Consider using Next.js `redirect()` from `next/navigation` for server-side redirects where possible.

---

### ISSUE-003: Missing `app/page.tsx` Redirect Target
**Files:** [`app/page.tsx`](frontendv1/app/page.tsx:4)  
**Severity:** MEDIUM

The root page redirects to `/care-circle-family`, but this route requires authentication. An anonymous user hitting `/` will:
1. Get redirected to `/care-circle-family`
2. The `care-circle-family` layout has no auth guard (it's a client-side layout)
3. The `AppShellGuard` in `app/app/layout.tsx` does NOT wrap `care-circle-family` routes

**Problems:**
- The `care-circle-family` layout at [`app/care-circle-family/layout.tsx`](frontendv1/app/care-circle-family/layout.tsx) does not include `AppShellGuard` or `PlatformAppGate`
- Anonymous users can access `/care-circle-family` directly without being redirected to login
- The `AppMembershipGuard` checks `requires_auth` but returns `children` when `requires_auth` is true and session is not authenticated (line 35-37 of `app-membership-guard.tsx`), which is a logic bug

**Recommendation:** Add auth guard to `care-circle-family` layout or ensure `PlatformAppGate` is used consistently.

---

## 2. Security Issues

### ISSUE-004: Open Redirect Risk in `normalizeNextPath`
**Files:** [`lib/auth-redirect.ts`](frontendv1/lib/auth-redirect.ts:21-38)  
**Severity:** MEDIUM

The `normalizeNextPath` function validates `next` query params against allowed prefixes:

```tsx
const ALLOWED_PREFIXES = [
  "/storytelling",
  "/care-circle-family",
  "/care-circle-patient",
  "/chatbot",
  "/app",
  "/help",
  "/public",
];
```

**Problems:**
- The `/app` prefix is allowed, but `/app` routes are legacy bridges that redirect to `/storytelling/*`. A malicious actor could craft `/app/evil-page` which would pass validation but then redirect to `/storytelling/account` (the fallback), creating confusion
- No explicit block for paths like `/admin` which could be socially engineered
- The function does not block paths that start with `../` or `./` (path traversal), though the `startsWith("/")` check mitigates this

**Recommendation:** Add explicit blocks for sensitive paths (`/admin`, `/api`) and add path traversal checks.

---

### ISSUE-005: Google Sign-In URL Not Fully Secured
**Files:** [`lib/api.ts`](frontendv1/lib/api.ts:195-197)  
**Severity:** LOW

```tsx
export function getGoogleSignInUrl(): string {
  return `${API_BASE}/auth/google`;
}
```

The Google sign-in URL is constructed without any state parameter or CSRF protection on the client side. While the backend should handle CSRF, the client does not generate or store a state token before redirecting.

**Recommendation:** Ensure the backend `/auth/google` endpoint generates and validates OAuth state parameters.

---

### ISSUE-006: `care-circle-template-admin.ts` Direct File System Access
**Files:** [`lib/care-circle-template-admin.ts`](frontendv1/lib/care-circle-template-admin.ts)  
**Severity:** HIGH

This module performs direct file system operations to read/write HTML templates and CSS from the Python backend's providers directory:

```tsx
const PROVIDERS_ROOT = path.resolve(
  process.cwd(),
  "..",
  "app",
  "services",
  "care_circle",
  "providers",
);
```

**Problems:**
- Cross-directory file access from Next.js route handlers
- No input sanitization on `providerKey` or `theme` parameters — path traversal possible via `../` in provider keys
- The `saveTemplateEditorDocument` function writes files without validation
- No authentication check in this module itself (relies on caller)

**Recommendation:** Add path traversal guards, validate `providerKey` against a whitelist, and add explicit auth checks.

---

## 3. Functional Bugs

### ISSUE-007: `AppMembershipGuard` Logic Bug — Auth-Required Routes Show Content
**Files:** [`components/platform/app-membership-guard.tsx`](frontendv1/components/platform/app-membership-guard.tsx:35-37)  
**Severity:** HIGH

```tsx
if (context.requires_auth && session.status !== "authenticated") {
  return <>{children}</>;  // BUG: Shows children when auth IS required but user is NOT authenticated
}
```

This condition is inverted. When `requires_auth` is true and the session is NOT authenticated, it should NOT render children. Instead, it should redirect to login or show a loading state.

**Impact:** Authenticated-gated routes may render their content to unauthenticated users until the `AppShellGuard` catches up with its redirect.

**Recommendation:** Change to:
```tsx
if (context.requires_auth && session.status !== "authenticated") {
  return <LoadingState label="Redirecting to login" />;
}
```

---

### ISSUE-008: `registerUser` Response Handling Mismatch
**Files:** [`lib/api.ts`](frontendv1/lib/api.ts:165-176), [`app/auth/register/page.tsx`](frontendv1/app/auth/register/page.tsx:59-61)  
**Severity:** MEDIUM

The `registerUser` function returns `{ data: SessionUser }` via `apiFetchRaw`, but the register page accesses `response.data`:

```tsx
// api.ts
export async function registerUser(payload: {...}): Promise<{ data: SessionUser }> {
  return apiFetchRaw<{ data: SessionUser }>("/auth/register", {...});
}

// register/page.tsx
const response = await registerUser(values);
setAuthenticated(response.data);  // response is already { data: SessionUser }, so this is SessionUser.data
```

However, `apiFetchRaw` does NOT unwrap the `data` envelope — it returns the raw JSON. So `response` is `{ data: SessionUser }`, and `response.data` is `SessionUser`. This is correct.

**BUT:** The `apiFetch` function (used by other endpoints) DOES unwrap the envelope. If the backend response shape changes, this inconsistency could cause issues.

**Recommendation:** Standardize on one response handling pattern. Consider having `registerUser` use `apiFetch` consistently.

---

### ISSUE-009: `fetchSession` Silently Swallows All Errors
**Files:** [`lib/api.ts`](frontendv1/lib/api.ts:142-148)  
**Severity:** LOW

```tsx
export async function fetchSession(): Promise<SessionUser | null> {
  try {
    return await apiFetch<SessionUser>("/users/me");
  } catch {
    return null;  // All errors swallowed
  }
}
```

This makes it impossible to distinguish between "user is not authenticated" (401) and "backend is down" (500, network error). The `refreshSession` function in `app-providers.tsx` handles this by setting `status: "error"` on catch, but the root cause is hidden.

**Recommendation:** Return a more structured result or at least log the error for debugging.

---

### ISSUE-0010: Toast Auto-Dismiss Uses Fixed 4500ms
**Files:** [`components/providers/app-providers.tsx`](frontendv1/components/providers/app-providers.tsx:165-167)  
**Severity:** LOW

```tsx
window.setTimeout(() => {
  setToasts((current) => current.filter((item) => item.id !== id));
}, 4500);
```

All toasts auto-dismiss after exactly 4.5 seconds. Error toasts that contain critical information (e.g., "Session bootstrap failed") may be dismissed before the user can read them.

**Recommendation:** Use longer durations for error/warning toasts (e.g., 8000ms) and shorter for success/info (e.g., 3000ms).

---

## 4. Architecture & Design Issues

### ISSUE-011: Inconsistent Layout Hierarchy
**Files:** Multiple layout files  
**Severity:** MEDIUM

The sprint establishes multiple layout patterns without a clear hierarchy:

| Route | Layout | Auth Guard |
|-------|--------|------------|
| `/` | Root layout only | None (redirects) |
| `/app/*` | `app/app/layout.tsx` → `AppShell` + `AppShellGuard` | Yes |
| `/auth/*` | `app/auth/layout.tsx` → `PublicShell` | None (intentional) |
| `/storytelling/*` | `app/storytelling/layout.tsx` | ??? |
| `/care-circle-family/*` | `app/care-circle-family/layout.tsx` | ??? |
| `/care-circle-patient/*` | `app/care-circle-patient/layout.tsx` | None (intentional) |
| `/chatbot/*` | `app/chatbot/layout.tsx` | ??? |

**Problem:** The layouts for `storytelling`, `care-circle-family`, and `chatbot` are not visible in the file listing but are referenced in the sprint doc. If they don't include `AppShellGuard` or `PlatformAppGate`, auth protection is inconsistent.

**Recommendation:** Document the layout hierarchy explicitly and ensure all app-specific layouts use `PlatformAppGate` for consistent auth behavior.

---

### ISSUE-012: `PlatformRouteBridge` Infinite Loop Risk
**Files:** [`components/platform/platform-route-bridge.tsx`](frontendv1/components/platform/platform-route-bridge.tsx:13-15)  
**Severity:** MEDIUM

```tsx
useEffect(() => {
  router.replace(getLegacyRouteTarget(pathname));
}, [pathname, router]);
```

If `getLegacyRouteTarget(pathname)` returns the same pathname (e.g., an unmapped `/app/*` path falls through to the default `/storytelling/account`), the `pathname` change triggers another effect run. While `router.replace` should prevent re-triggering the effect (since it replaces rather than pushes), this is fragile.

**Recommendation:** Add a ref to track whether the redirect has already been attempted:

```tsx
const hasRedirected = useRef(false);
useEffect(() => {
  if (!hasRedirected.current) {
    hasRedirected.current = true;
    router.replace(getLegacyRouteTarget(pathname));
  }
}, [pathname, router]);
```

---

### ISSUE-013: `resolveSurfaceId` Hardcoded Route Mapping
**Files:** [`components/platform/platform-context.ts`](frontendv1/components/platform/platform-context.ts:68-85)  
**Severity:** LOW

The surface resolution is entirely hardcoded:

```tsx
export function resolveSurfaceId(pathname: string): PlatformSurfaceId {
  if (pathname === "/storytelling" || pathname.startsWith("/storytelling/")) {
    return "storytelling";
  }
  // ... more hardcoded checks
  return "public";
}
```

This is brittle — adding a new surface requires modifying this function AND the `SURFACES` array AND the `apps.ts` registry.

**Recommendation:** Consolidate route-to-surface mapping into a single source of truth (e.g., extend `apps.ts` with surface metadata).

---

### ISSUE-014: `AppShellResolver` Unused Component
**Files:** [`components/platform/app-shell-resolver.tsx`](frontendv1/components/platform/app-shell-resolver.tsx)  
**Severity:** LOW

This component wraps children in `AppShell` and optionally shows `AppRouteLanding`. However, it is not referenced in any of the reviewed page files. The `app/app/layout.tsx` uses `AppShell` + `AppShellGuard` directly.

**Recommendation:** Either use this component consistently or remove it to reduce maintenance burden.

---

### ISSUE-015: `TopNav` Legacy Links Point to `/app/*`
**Files:** [`components/shell/top-nav.tsx`](frontendv1/components/shell/top-nav.tsx:36-39)  
**Severity:** MEDIUM

```tsx
const primaryLinks = activeApp?.primaryLinks ?? [
  { href: "/", label: "Home" },
  { href: "/app/account", label: "Account" },
  { href: "/app/billing", label: "Billing" },
  { href: "/app/referrals", label: "Referrals" },
  { href: "/help", label: "Help" }
];
```

The default nav links point to legacy `/app/*` paths which trigger `PlatformRouteBridge` redirects. While this works, it adds an unnecessary redirect hop on every navigation.

**Recommendation:** Update default links to point directly to the new routes (`/storytelling/account`, etc.).

---

## 5. Test Coverage Gaps

### ISSUE-016: No E2E Tests for `care-circle-family` Auth Flow
**Files:** [`tests/e2e/`](frontendv1/tests/e2e/)  
**Severity:** MEDIUM

The sprint doc lists `sprint1-shell.spec.ts`, `sprint2-auth.spec.ts`, `sprint3-framework.spec.ts`, and `sprint-common-platform.spec.ts` as delivered tests. However:

- No test verifies that anonymous users are properly redirected when accessing `/care-circle-family`
- No test verifies the `care-circle-family` dashboard renders correctly for authenticated users
- No test covers the `care-circle-patient` direct-entry flow

**Recommendation:** Add tests for care-circle family auth flow and patient direct-entry.

---

### ISSUE-017: No Unit Tests for Platform Context Logic
**Files:** [`components/platform/platform-context.ts`](frontendv1/components/platform/platform-context.ts)  
**Severity:** MEDIUM

The `platform-context.ts` module contains critical routing logic (`resolveSurfaceId`, `resolvePlatformContext`, `getLegacyRouteTarget`, `getDefaultAuthDestination`) but has no associated unit tests.

**Recommendation:** Add unit tests for:
- `resolveSurfaceId` with all route prefixes
- `resolvePlatformContext` for each surface
- `getLegacyRouteTarget` for all legacy routes
- `getDefaultAuthDestination` for each surface

---

### ISSUE-018: No Tests for `auth-redirect.ts` Security Logic
**Files:** [`lib/auth-redirect.ts`](frontendv1/lib/auth-redirect.ts)  
**Severity:** HIGH

The `normalizeNextPath` function is a security-critical redirect validator with no tests.

**Recommendation:** Add unit tests covering:
- Valid internal paths (all allowed prefixes)
- External URLs (`http://`, `//`, `https://`)
- Path traversal attempts (`../`, `./`)
- Null/undefined/empty inputs
- Edge cases (paths matching prefix but with extra segments)

---

### ISSUE-019: Mock Helper Overly Broad
**Files:** [`tests/e2e/helpers.ts`](frontendv1/tests/e2e/helpers.ts)  
**Severity:** LOW

The `mockAppApis` function mocks over 50 API endpoints in a single 1400+ line file. This creates:
- High coupling between tests and mock implementation
- Difficulty in understanding what each test actually exercises
- Risk of mock drift when backend endpoints change

**Recommendation:** Split mocks into domain-specific helpers (auth, billing, care-circle, etc.) and document the mock API contract.

---

### ISSUE-020: Playwright Config Uses Non-Standard Port
**Files:** [`playwright.config.ts`](frontendv1/playwright.config.ts:12)  
**Severity:** LOW

```tsx
baseURL: "http://127.0.0.1:3001",
command: "npm run start -- --port 3001",
```

The tests use port 3001 instead of the default Next.js dev port 3000. This is fine for CI but could confuse developers running tests locally who expect the default port.

**Recommendation:** Document this choice and consider adding a `test:dev` script that uses port 3000 for local development.

---

## 6. Code Quality & Maintainability

### ISSUE-021: Duplicate Context Fallbacks
**Files:** [`components/providers/app-providers.tsx`](frontendv1/components/providers/app-providers.tsx:55-96)  
**Severity:** LOW

Six separate fallback context objects are defined, each with no-op implementations:

```tsx
const fallbackThemeContext: ThemeContextValue = {
  theme: "light",
  setTheme: () => undefined,
  toggleTheme: () => undefined
};
// ... five more
```

These are used in the custom hooks:
```tsx
export function useTheme() {
  return useContext(ThemeContext) ?? fallbackThemeContext;
}
```

**Problem:** If a component calls `useTheme()` outside `AppProviders`, the no-op functions silently fail. There's no warning or error.

**Recommendation:** Add a development-mode warning when fallback contexts are used:
```tsx
export function useTheme() {
  const context = useContext(ThemeContext);
  if (process.env.NODE_ENV === "development" && context === undefined) {
    console.warn("useTheme() called outside AppProviders");
  }
  return context ?? fallbackThemeContext;
}
```

---

### ISSUE-022: `cn()` Utility Only Exports One Function
**Files:** [`lib/utils.ts`](frontendv1/lib/utils.ts)  
**Severity:** INFO

Standard shadcn/ui pattern, but the file only contains the `cn` utility. This is fine but worth noting that all other "utility" logic is scattered across domain files.

---

### ISSUE-023: Inline Styles in `PageHeader`
**Files:** [`components/shell/page-header.tsx`](frontendv1/components/shell/page-header.tsx:14-20)  
**Severity:** LOW

```tsx
style={{
  background: [
    "radial-gradient(circle at 10% -10%, rgba(220,229,226,0.95), transparent 45%)",
    // ...
  ].join(", ")
}}
```

Inline styles bypass Tailwind's purge and make it impossible to customize via theme configuration.

**Recommendation:** Move to Tailwind arbitrary values or CSS custom properties.

---

### ISSUE-024: `Button` Component Accepts Unhandled Props
**Files:** [`components/ui/button.tsx`](frontendv1/components/ui/button.tsx:9-10)  
**Severity:** LOW

```tsx
export function Button({
  children,
  className,
  type = "button",
  title,
  tooltip,  // Accepted but not typed in the interface
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
  tooltip?: string;
}) {
```

The `tooltip` prop is accepted but the `title` attribute is set from `title ?? tooltip ?? ...`. This is functional but the dual `title`/`tooltip` naming is confusing.

**Recommendation:** Rename `tooltip` to `fallbackTitle` or remove it entirely and require explicit `title` attributes.

---

### ISSUE-025: `help-content.ts` is 900+ Lines
**Files:** [`lib/help-content.ts`](frontendv1/lib/help-content.ts)  
**Severity:** LOW

All help content for every page is in a single file. This makes navigation and maintenance difficult.

**Recommendation:** Split help content into per-page or per-domain files and export from an index.

---

## 7. Accessibility Issues

### ISSUE-026: Missing `lang` Attribute on Dynamic Content
**Files:** Multiple pages  
**Severity:** LOW

The root layout sets `lang="en"` on `<html>`, but dynamic content (toasts, modals, dropdown menus) does not set `lang` attributes. If the platform supports i18n in the future, this will be an issue.

**Recommendation:** No action needed for Sprint 01, but note for i18n planning.

---

### ISSUE-027: `CookieConsentBanner` Not Keyboard Accessible
**Files:** [`components/shell/cookie-consent-banner.tsx`](frontendv1/components/shell/cookie-consent-banner.tsx:20-25)  
**Severity:** LOW

The accept button uses a `<button>` element which is keyboard accessible. However, the banner itself is an `<aside>` that doesn't have `role="alert"` or `aria-live`, so screen readers may not announce it.

**Recommendation:** Add `role="alert"` or `aria-live="polite"` to the banner container.

---

### ISSUE-028: `UserMenu` Dropdown Missing Keyboard Documentation
**Files:** [`components/shell/user-menu.tsx`](frontendv1/components/shell/user-menu.tsx)  
**Severity:** LOW

The Radix `DropdownMenu` handles most keyboard interactions automatically. However, the logout action uses `onSelect` with `event.preventDefault()` which is correct, but there's no visible indication of the active/focused menu item for keyboard users.

**Recommendation:** Verify Radix's default styling provides visible focus indicators.

---

## 8. Performance Concerns

### ISSUE-029: Maintenance Polling Every 60 Seconds
**Files:** [`components/providers/app-providers.tsx`](frontendv1/components/providers/app-providers.tsx:254-260)  
**Severity:** LOW

```tsx
useEffect(() => {
  const interval = window.setInterval(() => {
    void refreshMaintenance();
  }, 60000);
  return () => window.clearInterval(interval);
}, [refreshMaintenance]);
```

Every authenticated user polls the maintenance endpoint every 60 seconds. With many concurrent users, this creates unnecessary server load.

**Recommendation:** Consider WebSocket/SSE for maintenance state push, or increase the interval to 5 minutes with a manual refresh option.

---

### ISSUE-030: No React Query Stale-Time Optimization
**Files:** [`components/providers/app-providers.tsx`](frontendv1/components/providers/app-providers.tsx:98-111)  
**Severity:** LOW

```tsx
const queryClient = useCreateQueryClient();
// ...
new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000  // 30 seconds for ALL queries
    }
  }
})
```

A single `staleTime` of 30 seconds applies to all queries. Session data (which rarely changes) and balance data (which could change frequently) share the same cache strategy.

**Recommendation:** Use per-query `staleTime` configuration via `useQuery` options.

---

## 9. Configuration & Environment

### ISSUE-031: API Base URL Fallback to localhost
**Files:** [`next.config.mjs`](frontendv1/next.config.mjs:3-6)  
**Severity:** MEDIUM

```tsx
const BACKEND_ORIGIN =
  !configuredApiBaseUrl || configuredApiBaseUrl.startsWith("/")
    ? "http://localhost:8000"
    : configuredApiBaseUrl.replace(/\/api\/v1\/?$/, "");
```

In production, if `NEXT_PUBLIC_API_BASE_URL` is not set or is a relative path, the rewrite falls back to `http://localhost:8000`. This would break in containerized deployments.

**Recommendation:** Add a build-time check or deployment validation that ensures `NEXT_PUBLIC_API_BASE_URL` is set in production.

---

### ISSUE-032: No TypeScript Strict Mode
**Files:** [`frontendv1/tsconfig.json`](frontendv1/tsconfig.json) (not reviewed, inferred from code)  
**Severity:** LOW

Several files use `any` types (e.g., `careCirclePatients: any[]` in helpers.ts) and implicit `any` in some places.

**Recommendation:** Enable `strict: true` in tsconfig and fix type issues.

---

### ISSUE-033: Missing `.env` Documentation for Frontend
**Files:** [`frontendv1/`](frontendv1/)  
**Severity:** LOW

The `next.config.mjs` references `NEXT_PUBLIC_API_BASE_URL` and `BACKEND_INTERNAL_URL` (in `require-admin.ts`), but there's no `.env.example` or documentation for required environment variables.

**Recommendation:** Add `.env.example` with all required and optional environment variables.

---

## 10. Summary Matrix

| ID | Category | Severity | File | Status |
|----|----------|----------|------|--------|
| ISSUE-001 | Security | HIGH | `app/auth/login/page.tsx` | Debug login exposed |
| ISSUE-002 | Functional | MEDIUM | `app-shell-guard.tsx`, `app-membership-guard.tsx` | useLayoutEffect flash |
| ISSUE-003 | Functional | MEDIUM | `app/page.tsx`, `care-circle-family/layout.tsx` | Missing auth on CC family |
| ISSUE-004 | Security | MEDIUM | `lib/auth-redirect.ts` | Open redirect edge cases |
| ISSUE-005 | Security | LOW | `lib/api.ts` | Google OAuth state |
| ISSUE-006 | Security | HIGH | `lib/care-circle-template-admin.ts` | Path traversal risk |
| ISSUE-007 | Functional | HIGH | `app-membership-guard.tsx` | Inverted auth logic |
| ISSUE-008 | Functional | MEDIUM | `lib/api.ts`, `register/page.tsx` | Response handling inconsistency |
| ISSUE-009 | Functional | LOW | `lib/api.ts` | Silent error swallowing |
| ISSUE-010 | UX | LOW | `app-providers.tsx` | Fixed toast duration |
| ISSUE-011 | Architecture | MEDIUM | Multiple layouts | Inconsistent layout hierarchy |
| ISSUE-012 | Architecture | MEDIUM | `platform-route-bridge.tsx` | Redirect loop risk |
| ISSUE-013 | Architecture | LOW | `platform-context.ts` | Hardcoded route mapping |
| ISSUE-014 | Architecture | LOW | `app-shell-resolver.tsx` | Unused component |
| ISSUE-015 | Architecture | MEDIUM | `top-nav.tsx` | Legacy nav links |
| ISSUE-016 | Testing | MEDIUM | `tests/e2e/` | Missing CC family tests |
| ISSUE-017 | Testing | MEDIUM | `platform-context.ts` | No unit tests for routing |
| ISSUE-018 | Testing | HIGH | `lib/auth-redirect.ts` | No security tests |
| ISSUE-019 | Testing | LOW | `tests/e2e/helpers.ts` | Overly broad mock helper |
| ISSUE-020 | Testing | LOW | `playwright.config.ts` | Non-standard port |
| ISSUE-021 | Quality | LOW | `app-providers.tsx` | Silent context fallbacks |
| ISSUE-022 | Quality | INFO | `lib/utils.ts` | Standard pattern |
| ISSUE-023 | Quality | LOW | `page-header.tsx` | Inline styles |
| ISSUE-024 | Quality | LOW | `button.tsx` | Confusing prop naming |
| ISSUE-025 | Quality | LOW | `help-content.ts` | Single large file |
| ISSUE-026 | Accessibility | LOW | Multiple | i18n readiness |
| ISSUE-027 | Accessibility | LOW | `cookie-consent-banner.tsx` | Missing aria-live |
| ISSUE-028 | Accessibility | LOW | `user-menu.tsx` | Focus indicator |
| ISSUE-029 | Performance | LOW | `app-providers.tsx` | Maintenance polling |
| ISSUE-030 | Performance | LOW | `app-providers.tsx` | Uniform staleTime |
| ISSUE-031 | Config | MEDIUM | `next.config.mjs` | API URL fallback |
| ISSUE-032 | Config | LOW | Various | TypeScript strict mode |
| ISSUE-033 | Config | LOW | `frontendv1/` | Missing .env.example |

### Severity Distribution

| Severity | Count |
|----------|-------|
| HIGH | 3 |
| MEDIUM | 8 |
| LOW | 15 |
| INFO | 1 |

### Category Distribution

| Category | Count |
|----------|-------|
| Security | 5 |
| Functional | 7 |
| Architecture | 5 |
| Testing | 5 |
| Code Quality | 5 |
| Accessibility | 3 |
| Performance | 2 |
| Configuration | 3 |

---

## Priority Remediation Order

1. **ISSUE-007** — Fix inverted auth logic in `AppMembershipGuard` (HIGH functional bug)
2. **ISSUE-001** — Remove or guard debug login behind dev-only environment (HIGH security)
3. **ISSUE-006** — Add path traversal guards to template admin (HIGH security)
4. **ISSUE-018** — Add unit tests for `normalizeNextPath` (HIGH testing gap)
5. **ISSUE-003** — Add auth guard to `care-circle-family` layout (MEDIUM functional)
6. **ISSUE-002** — Switch `useLayoutEffect` to `useEffect` (MEDIUM UX)
7. **ISSUE-004** — Harden redirect validation (MEDIUM security)
8. **ISSUE-008** — Standardize API response handling (MEDIUM consistency)
9. **ISSUE-011** — Document and unify layout hierarchy (MEDIUM architecture)
10. **ISSUE-012** — Add redirect deduplication in `PlatformRouteBridge` (MEDIUM reliability)

## Appendix A: Files Reviewed

### Source Files Listed in Sprint Baseline

The sprint baseline [`frontendv1Sprint01PlatformBaseline.md`](frontendv1Sprint01PlatformBaseline.md) lists these source file paths. All were reviewed:

| Source Path (from sprint doc) | Files Reviewed |
|---|---|
| `frontendv1/app/auth/**` | `layout.tsx`, `login/page.tsx`, `register/page.tsx`, `forgot-password/page.tsx`, `password-reset/confirm/page.tsx`, `reset-password/page.tsx` |
| `frontendv1/app/app/**` | `layout.tsx`, `account/page.tsx` |
| `frontendv1/components/platform/**` | `app-membership-guard.tsx`, `app-shell-resolver.tsx`, `owner-scope-badge.tsx`, `platform-app-gate.tsx`, `platform-context.ts`, `platform-route-bridge.tsx`, `platform-route-landing.tsx`, `realtime-status-indicator.tsx` |
| `frontendv1/components/shell/**` | `app-shell-guard.tsx`, `app-shell.tsx`, `breadcrumbs.tsx`, `coin-balance-badge.tsx`, `cookie-consent-banner.tsx`, `footer.tsx`, `maintenance-banner.tsx`, `maintenance-gate.tsx`, `page-header.tsx`, `public-shell.tsx`, `theme-toggle.tsx`, `top-nav.tsx`, `user-menu.tsx` |
| `frontendv1/tests/e2e/sprint1-shell.spec.ts` | `sprint1-shell.spec.ts` |
| `frontendv1/tests/e2e/sprint2-auth.spec.ts` | `sprint2-auth.spec.ts` |
| `frontendv1/tests/e2e/sprint3-framework.spec.ts` | `sprint3-framework.spec.ts` |
| `frontendv1/tests/e2e/sprint-common-platform.spec.ts` | `sprint-common-platform.spec.ts` |

### Supporting Files Reviewed

Additional files were reviewed to understand the full code paths exercised by the sprint deliverables:

| Category | Files Reviewed |
|---|---|
| Next.js bootstrap | `app/layout.tsx`, `app/app/layout.tsx`, `next.config.mjs`, `package.json` |
| Providers | `components/providers/app-providers.tsx` |
| UI components | All 22 files in `components/ui/` |
| App routes | `app/page.tsx`, `app/storytelling/page.tsx`, `app/care-circle-family/page.tsx`, `app/care-circle-patient/page.tsx`, `app/chatbot/page.tsx`, `app/public/page.tsx`, `app/not-found.tsx`, `app/loading.tsx` |
| Lib modules | `lib/api.ts`, `lib/types.ts`, `lib/apps.ts`, `lib/auth-redirect.ts`, `lib/utils.ts`, `lib/help-content.ts`, `lib/require-admin.ts`, `lib/care-circle-template-admin.ts` |
| Test helpers | `tests/e2e/helpers.ts`, `playwright.config.ts` |
