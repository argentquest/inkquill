"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { useSession } from "@/components/providers/app-providers";
import { AlertBanner } from "@/components/ui/alert-banner";
import { Button } from "@/components/ui/button";
import { PasswordField } from "@/components/ui/password-field";
import { TextField } from "@/components/ui/text-field";
import { joinFamily, registerUser } from "@/lib/api";

const joinSchema = z.object({
  join_code: z.string().min(3, "Enter the join code from the family owner.").max(20),
  username: z.string().min(3, "Username must be at least 3 characters."),
  email: z.string().email("Enter a valid email address."),
  display_name: z.string().min(2, "Display name must be at least 2 characters.").optional().or(z.literal("")),
  password: z.string().min(8, "Password must be at least 8 characters."),
  terms_accepted: z.boolean().refine((v) => v, "You must accept the Terms of Service."),
});

type JoinForm = z.infer<typeof joinSchema>;

type JoinState = "form" | "pending";

function normalizeJoinCode(value: string | null): string {
  return (value ?? "").toUpperCase().replace(/[^A-Z0-9]/g, "");
}

export default function JoinPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setAuthenticated } = useSession();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [joinState, setJoinState] = useState<JoinState>("form");
  const [familyName, setFamilyName] = useState<string>("");
  const inviteJoinCode = useMemo(() => normalizeJoinCode(searchParams.get("code")), [searchParams]);

  const form = useForm<JoinForm>({
    resolver: zodResolver(joinSchema),
    defaultValues: {
      join_code: "",
      username: "",
      email: "",
      display_name: "",
      password: "",
      terms_accepted: false,
    },
  });

  useEffect(() => {
    if (!inviteJoinCode) return;
    if (form.getValues("join_code")) return;

    form.setValue("join_code", inviteJoinCode, {
      shouldDirty: false,
      shouldTouch: false,
      shouldValidate: true,
    });
  }, [form, inviteJoinCode]);

  async function onSubmit(values: JoinForm) {
    setSubmitError(null);
    try {
      const regResponse = await registerUser({
        username: values.username,
        email: values.email,
        display_name: values.display_name,
        password: values.password,
        terms_accepted: values.terms_accepted,
      });
      setAuthenticated(regResponse.data);

      const joinResponse = await joinFamily(normalizeJoinCode(values.join_code));
      setFamilyName(joinResponse.family_name);
      setJoinState("pending");
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Something went wrong. Please try again.");
    }
  }

  if (joinState === "pending") {
    return (
      <section className="rounded-[32px] border border-black/10 bg-white/80 p-8 shadow-panel text-center">
        <div className="text-4xl mb-4">🏠</div>
        <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Request sent</p>
        <h1 className="mt-3 font-display text-3xl text-ink-900">You&apos;re almost in.</h1>
        <p className="mt-4 text-sm leading-7 text-ink-700 max-w-md mx-auto">
          Your account has been created and your request to join <strong>{familyName}</strong> has been sent to the family owner. You&apos;ll be able to access the family once they approve you.
        </p>
        <div className="mt-8">
          <Button onClick={() => router.push("/auth/login")} className="w-full max-w-xs">
            Go to sign in
          </Button>
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-[32px] border border-black/10 bg-white/80 p-8 shadow-panel">
      <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Family member registration</p>
      <h1 className="mt-3 font-display text-4xl text-ink-900">Join a care circle.</h1>
      <p className="mt-4 text-sm leading-7 text-ink-700">
        You&apos;re registering as a <strong>family member</strong> — not as the family owner. Ask your family owner for their join code, then create your account below.
      </p>

      <form className="mt-8 space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
        {submitError ? <AlertBanner title="Could not complete registration" detail={submitError} tone="error" /> : null}

        <div className="rounded-2xl border border-black/10 bg-black/[0.02] p-5 space-y-1">
          <p className="text-xs uppercase tracking-[0.24em] text-ink-600 mb-3">Step 1 — Enter your join code</p>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.24em] text-ink-600">Join code</span>
            <input
              autoComplete="off"
              className="mt-2 w-full rounded-[20px] border border-black/10 bg-white/85 px-4 py-3 text-sm text-ink-900 outline-none transition font-mono uppercase tracking-[0.18em] placeholder:text-ink-500 focus:border-ink-400 focus:ring-2 focus:ring-ink-200"
              placeholder="e.g. AB12CD"
              title="Join code. Enter or review this value."
              {...form.register("join_code")}
              onChange={(e) => form.setValue("join_code", normalizeJoinCode(e.target.value))}
            />
            {form.formState.errors.join_code?.message ? (
              <p className="mt-1 text-xs text-red-600">{form.formState.errors.join_code.message}</p>
            ) : null}
          </label>
          <p className="text-xs text-ink-500 pt-1">This is the code your family owner shares with you.</p>
        </div>

        <div className="rounded-2xl border border-black/10 bg-black/[0.02] p-5 space-y-4">
          <p className="text-xs uppercase tracking-[0.24em] text-ink-600">Step 2 — Create your account</p>
          <TextField label="Username" autoComplete="username" error={form.formState.errors.username?.message} {...form.register("username")} />
          <TextField label="Email" autoComplete="email" error={form.formState.errors.email?.message} {...form.register("email")} />
          <TextField label="Display name" autoComplete="nickname" error={form.formState.errors.display_name?.message} {...form.register("display_name")} />
          <PasswordField label="Password" autoComplete="new-password" error={form.formState.errors.password?.message} {...form.register("password")} />
          <label className="flex items-start gap-3 text-sm text-ink-700">
            <input
              className="mt-1 h-4 w-4"
              title="I accept the Terms of Service and want this account to be created. Toggle this option on or off."
              type="checkbox"
              {...form.register("terms_accepted")}
            />
            <span>I accept the Terms of Service and want this account to be created.</span>
          </label>
          {form.formState.errors.terms_accepted?.message ? (
            <AlertBanner title="Terms required" detail={form.formState.errors.terms_accepted.message} tone="warning" />
          ) : null}
        </div>

        <Button className="w-full" disabled={form.formState.isSubmitting} type="submit">
          {form.formState.isSubmitting ? "Creating account and sending request..." : "Create account and request to join"}
        </Button>
      </form>

      <div className="mt-6 text-sm text-ink-700 space-y-1">
        <p>
          <Link className="transition hover:text-ink-900" href="/auth/login">
            Already have an account? Sign in
          </Link>
        </p>
        <p>
          <Link className="transition hover:text-ink-900" href="/auth/register">
            Setting up a new family? Register here instead
          </Link>
        </p>
      </div>
    </section>
  );
}
