import { resolveApp } from "@/lib/apps";
import type { AppMembership, PlatformCurrentContext, PlatformSurfaceId, SessionState } from "@/lib/types";

interface SurfaceDefinition {
  surface_id: PlatformSurfaceId;
  app_id?: string | null;
  requires_auth: boolean;
  owner_scope: PlatformCurrentContext["owner_scope"];
  title: string;
  description: string;
}

const SURFACES: SurfaceDefinition[] = [
  {
    surface_id: "storytelling",
    app_id: "storytelling",
    requires_auth: true,
    owner_scope: "user",
    title: "Storytelling",
    description: "Creative authoring stays on the user-owned storytelling surface."
  },
  {
    surface_id: "care-circle-family",
    app_id: "care-circle",
    requires_auth: true,
    owner_scope: "family",
    title: "Care Circle Family",
    description: "Family-side coordination, events, patients, and household-owned billing live here."
  },
  {
    surface_id: "care-circle-patient",
    app_id: "care-circle",
    requires_auth: false,
    owner_scope: "patient",
    title: "Care Circle Patient",
    description: "Patient access stays simplified and direct-entry by design."
  },
  {
    surface_id: "chatbot",
    app_id: "chatbot",
    requires_auth: true,
    owner_scope: "user",
    title: "Chatbot",
    description: "Chatbot remains independent, but can still consume shared platform behavior."
  },
  {
    surface_id: "legacy-app",
    app_id: "storytelling",
    requires_auth: true,
    owner_scope: "user",
    title: "Legacy App Route",
    description: "Legacy shared app routes should bridge into the correct app-specific surface."
  },
  {
    surface_id: "public",
    app_id: null,
    requires_auth: false,
    owner_scope: "none",
    title: "Public Platform",
    description: "Public routes remain outside app-specific trees."
  }
];

function getSurfaceDefinition(surfaceId: PlatformSurfaceId) {
  return SURFACES.find((surface) => surface.surface_id === surfaceId) ?? SURFACES[SURFACES.length - 1];
}

export function resolveSurfaceId(pathname: string): PlatformSurfaceId {
  if (pathname === "/storytelling" || pathname.startsWith("/storytelling/")) {
    return "storytelling";
  }
  if (pathname === "/care-circle-family" || pathname.startsWith("/care-circle-family/")) {
    return "care-circle-family";
  }
  if (pathname === "/care-circle-patient" || pathname.startsWith("/care-circle-patient/")) {
    return "care-circle-patient";
  }
  if (pathname === "/chatbot" || pathname.startsWith("/chatbot/")) {
    return "chatbot";
  }
  if (pathname === "/app" || pathname.startsWith("/app/")) {
    return "legacy-app";
  }
  return "public";
}

function buildMemberships(session: SessionState): AppMembership[] {
  const isAuthenticated = session.status === "authenticated";

  return [
    { surface_id: "storytelling", granted: isAuthenticated, reason: isAuthenticated ? null : "Login required" },
    { surface_id: "care-circle-family", granted: isAuthenticated, reason: isAuthenticated ? null : "Login required" },
    { surface_id: "care-circle-patient", granted: true, reason: null },
    { surface_id: "chatbot", granted: isAuthenticated, reason: isAuthenticated ? null : "Login required" }
  ];
}

export function resolvePlatformContext(pathname: string, session: SessionState): PlatformCurrentContext {
  const surfaceId = resolveSurfaceId(pathname);
  const surface = getSurfaceDefinition(surfaceId);
  const app = resolveApp(pathname);

  return {
    surface_id: surface.surface_id,
    app_id: app?.id ?? surface.app_id ?? null,
    requires_auth: surface.requires_auth,
    owner_scope: surface.owner_scope,
    title: surface.title,
    description: surface.description,
    memberships: buildMemberships(session)
  };
}

export function getDefaultAuthDestination(surfaceId: PlatformSurfaceId) {
  switch (surfaceId) {
    case "care-circle-family":
      return "/care-circle-family";
    case "care-circle-patient":
      return "/care-circle-patient";
    case "chatbot":
      return "/chatbot";
    case "storytelling":
    case "legacy-app":
      return "/storytelling/account";
    default:
      return "/storytelling/account";
  }
}

export function getLegacyRouteTarget(pathname: string) {
  if (pathname === "/app/account") {
    return "/storytelling/account";
  }
  if (pathname === "/app/account/edit") {
    return "/storytelling/account/edit";
  }
  if (pathname === "/app/billing") {
    return "/storytelling/billing";
  }
  if (pathname === "/app/referrals") {
    return "/storytelling/referrals";
  }
  if (pathname === "/app/onboarding") {
    return "/storytelling/onboarding";
  }

  return "/storytelling/account";
}
