/**
 * App feature flags — driven by NEXT_PUBLIC_*_ENABLED env vars.
 * Defaults to true when the variable is absent so new environments
 * don't accidentally disable everything.
 */
function flag(envVar: string | undefined): boolean {
  return envVar !== "false";
}

export const features = {
  storytelling: flag(process.env.NEXT_PUBLIC_STORYTELLING_ENABLED),
  careCircle: flag(process.env.NEXT_PUBLIC_CARE_CIRCLE_ENABLED),
  chat: flag(process.env.NEXT_PUBLIC_CHAT_ENABLED),
} as const;
