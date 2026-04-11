"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { AlertBanner } from "@/components/ui/alert-banner";
import { Button } from "@/components/ui/button";
import { GoogleSigninButton } from "@/components/ui/google-signin-button";
import { PasswordField } from "@/components/ui/password-field";
import { TextField } from "@/components/ui/text-field";
import { normalizeNextPath } from "@/lib/auth-redirect";
import { fetchSession, loginUser } from "@/lib/api";

const DEBUG_ACCOUNTS = [
  { label: "Maple Grove — Clara (owner)", username: "ericsilvertx+clara@gmail.com" },
  { label: "Harbor Point — Olivia (owner)", username: "olivia.harbor@example.com" },
  { label: "Sunset Ridge — Sophie (owner)", username: "ericsilvertx+sophie@gmail.com" },
] as const;

const DEBUG_PASSWORD = "password123";

const loginSchema = z.object({
  username: z.string().min(3, "Enter your username."),
  password: z.string().min(8, "Password must be at least 8 characters.")
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = useMemo(() => normalizeNextPath(searchParams.get("next")), [searchParams]);
  const registerHref = useMemo(() => `/auth/register?next=${encodeURIComponent(next)}`, [next]);
  const { setAuthenticated, status } = useSession();
  const { pushToast } = useToasts();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [debugAccount, setDebugAccount] = useState<string>(DEBUG_ACCOUNTS[0].username);
  const [debugLoading, setDebugLoading] = useState(false);
  const form = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: ""
    }
  });

  useEffect(() => {
    if (status === "authenticated") {
      router.replace(next);
    }
  }, [next, router, status]);

  async function handleDebugLogin() {
    setDebugLoading(true);
    setSubmitError(null);
    try {
      await loginUser({ username: debugAccount, password: DEBUG_PASSWORD });
      const user = await fetchSession();
      if (!user) throw new Error("Session unavailable after debug login.");
      setAuthenticated(user);
      pushToast({ title: "Debug login", tone: "success", detail: `Signed in as ${debugAccount}` });
      router.replace("/care-circle-family");
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Debug login failed.");
    } finally {
      setDebugLoading(false);
    }
  }

  async function onSubmit(values: LoginForm) {
    setSubmitError(null);
    try {
      await loginUser(values);
      const user = await fetchSession();
      if (!user) {
        throw new Error("Authenticated session was not available after login.");
      }
      setAuthenticated(user);
      pushToast({ title: "Signed in", tone: "success", detail: "Your account shell is ready." });
      router.replace(next);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Unable to sign in.");
    }
  }

  return (
    <section className="rounded-[32px] border border-black/10 bg-white/80 p-8 shadow-panel">
      <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Authentication</p>
      <h1 className="mt-3 font-display text-4xl text-ink-900">Sign in to continue your work.</h1>
      <p className="mt-4 text-sm leading-7 text-ink-700">
        Sprint 2 keeps auth entry explicit, keyboard-friendly, and aligned with the account landing flow.
      </p>
      <form className="mt-8 space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
        {submitError ? <AlertBanner title="Login failed" detail={submitError} tone="error" /> : null}
        <TextField label="Username" autoComplete="username" error={form.formState.errors.username?.message} {...form.register("username")} />
        <PasswordField label="Password" autoComplete="current-password" error={form.formState.errors.password?.message} {...form.register("password")} />
        <Button className="w-full" disabled={form.formState.isSubmitting} type="submit">
          {form.formState.isSubmitting ? "Signing in..." : "Sign in"}
        </Button>
      </form>
      <div className="mt-6">
        <GoogleSigninButton />
      </div>
      <div className="mt-6 flex flex-wrap items-center justify-between gap-3 text-sm text-ink-700">
        <Link className="transition hover:text-ink-900" href="/auth/forgot-password">
          Forgot your password?
        </Link>
        <Link className="transition hover:text-ink-900" href={registerHref}>
          Need an account? Register
        </Link>
      </div>

      {/* ── Debug panel (dev only) ── */}
      <div className="mt-8 rounded-2xl border border-dashed border-amber-300 bg-amber-50/60 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-700">
          Dev · Quick login
        </p>
        <p className="mt-1 text-xs text-amber-600">
          Seed accounts — password <span className="font-mono">password123</span>
        </p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
          <select
            className="flex-1 rounded-xl border border-amber-200 bg-white px-3 py-2 text-sm text-ink-900 outline-none focus:border-amber-400"
            value={debugAccount}
            onChange={(e) => setDebugAccount(e.target.value)}
          >
            {DEBUG_ACCOUNTS.map((account) => (
              <option key={account.username} value={account.username}>
                {account.label}
              </option>
            ))}
          </select>
          <button
            className="inline-flex items-center justify-center rounded-xl bg-amber-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={debugLoading}
            onClick={handleDebugLogin}
            type="button"
          >
            {debugLoading ? "Logging in…" : "Login"}
          </button>
        </div>
      </div>
    </section>
  );
}
