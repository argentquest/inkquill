"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { AlertBanner } from "@/components/ui/alert-banner";
import { Button } from "@/components/ui/button";
import { PasswordField } from "@/components/ui/password-field";
import { confirmPasswordReset } from "@/lib/api";

const resetSchema = z
  .object({
    password: z.string().min(8, "Password must be at least 8 characters."),
    confirmPassword: z.string().min(8, "Confirm your new password.")
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: "Passwords must match.",
    path: ["confirmPassword"]
  });

type ResetForm = z.infer<typeof resetSchema>;

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const form = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
    defaultValues: {
      password: "",
      confirmPassword: ""
    }
  });

  async function onSubmit(values: ResetForm) {
    setSubmitError(null);
    setSubmitSuccess(null);
    try {
      const response = await confirmPasswordReset({ token, new_password: values.password });
      setSubmitSuccess(response.message);
      form.reset();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Unable to reset password.");
    }
  }

  return (
    <section className="rounded-[32px] border border-black/10 bg-white/80 p-8 shadow-panel">
      <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Recovery</p>
      <h1 className="mt-3 font-display text-4xl text-ink-900">Choose a new password.</h1>
      <p className="mt-4 text-sm leading-7 text-ink-700">
        This route reads the reset token from the URL and submits the new password to the backend confirm endpoint.
      </p>
      {!token ? <AlertBanner title="Missing token" detail="Open this page from a valid password reset link." tone="warning" /> : null}
      <form className="mt-8 space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
        {submitError ? <AlertBanner title="Reset failed" detail={submitError} tone="error" /> : null}
        {submitSuccess ? <AlertBanner title="Password reset complete" detail={submitSuccess} tone="success" /> : null}
        <PasswordField label="New password" autoComplete="new-password" error={form.formState.errors.password?.message} {...form.register("password")} />
        <PasswordField label="Confirm password" autoComplete="new-password" error={form.formState.errors.confirmPassword?.message} {...form.register("confirmPassword")} />
        <Button className="w-full" disabled={form.formState.isSubmitting || !token} type="submit">
          {form.formState.isSubmitting ? "Updating password..." : "Reset password"}
        </Button>
      </form>
      <div className="mt-6 text-sm text-ink-700">
        <Link className="transition hover:text-ink-900" href="/auth/login">
          Back to sign in
        </Link>
      </div>
    </section>
  );
}
