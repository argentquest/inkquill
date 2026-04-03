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
    </section>
  );
}
