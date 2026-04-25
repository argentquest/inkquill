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
import { HelpModal } from "@/components/ui/help-modal";
import { registerHelp } from "@/lib/help-content";
import { PasswordField } from "@/components/ui/password-field";
import { TextField } from "@/components/ui/text-field";
import { normalizeNextPath } from "@/lib/auth-redirect";
import { registerUser } from "@/lib/api";

const registerSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters."),
  email: z.string().email("Enter a valid email address."),
  display_name: z.string().min(2, "Display name must be at least 2 characters.").optional().or(z.literal("")),
  password: z.string().min(8, "Password must be at least 8 characters."),
  terms_accepted: z.boolean().refine((value) => value, "You must accept the Terms of Service.")
});

type RegisterForm = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = useMemo(() => normalizeNextPath(searchParams.get("next")), [searchParams]);
  const loginHref = useMemo(() => `/auth/login?next=${encodeURIComponent(next)}`, [next]);
  const { setAuthenticated, status } = useSession();
  const { pushToast } = useToasts();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const form = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: "",
      email: "",
      display_name: "",
      password: "",
      terms_accepted: false
    }
  });

  useEffect(() => {
    if (status === "authenticated") {
      router.replace(next);
    }
  }, [next, router, status]);

  async function onSubmit(values: RegisterForm) {
    setSubmitError(null);
    try {
      const response = await registerUser(values);
      setAuthenticated(response.data);
      pushToast({ title: "Account created", tone: "success", detail: "You are signed in and ready to go." });
      router.replace(next);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Unable to create your account.");
    }
  }

  return (
    <section className="rounded-[32px] border border-black/10 bg-white/80 p-8 shadow-panel">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Authentication</p>
          <h1 className="mt-3 font-display text-4xl text-ink-900">Create your writing account.</h1>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            Register through the React entry flow and land directly in the new account shell.
          </p>
        </div>
        <HelpModal helpContent={registerHelp} triggerLabel="Help" />
      </div>
      <form className="mt-8 space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
        {submitError ? <AlertBanner title="Registration failed" detail={submitError} tone="error" /> : null}
        <TextField
          label="Username"
          autoComplete="username"
          error={form.formState.errors.username?.message}
          tooltip="Choose a unique username at least 3 characters long. This will be your unique identifier on the platform."
          showTooltip
          {...form.register("username")}
        />
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          error={form.formState.errors.email?.message}
          tooltip="Enter a valid email address. This will be used for account verification and password resets."
          showTooltip
          {...form.register("email")}
        />
        <TextField
          label="Display name"
          type="text"
          autoComplete="nickname"
          error={form.formState.errors.display_name?.message}
          tooltip="This is the name other users will see. It can be your real name or a pseudonym. Optional."
          showTooltip
          {...form.register("display_name")}
        />
        <PasswordField
          label="Password"
          autoComplete="new-password"
          error={form.formState.errors.password?.message}
          tooltip="Create a strong password with at least 8 characters. Use a mix of uppercase, lowercase, numbers, and special characters."
          showTooltip
          {...form.register("password")}
        />
        <label className="flex items-start gap-3 text-sm text-ink-700">
          <input className="mt-1 h-4 w-4" type="checkbox" {...form.register("terms_accepted")} />
          <span>I accept the Terms of Service and want this account to be created.</span>
        </label>
        {form.formState.errors.terms_accepted?.message ? (
          <AlertBanner title="Terms required" detail={form.formState.errors.terms_accepted.message} tone="warning" />
        ) : null}
        <Button className="w-full" disabled={form.formState.isSubmitting} type="submit">
          {form.formState.isSubmitting ? "Creating account..." : "Create account"}
        </Button>
      </form>
      <div className="mt-6">
        <GoogleSigninButton />
      </div>
      <div className="mt-6 text-sm text-ink-700">
        <Link className="transition hover:text-ink-900" href={loginHref}>
          Already have an account? Sign in
        </Link>
      </div>
    </section>
  );
}
