"use client";

import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { AlertBanner } from "@/components/ui/alert-banner";
import { Button } from "@/components/ui/button";
import { HelpModal } from "@/components/ui/help-modal";
import { forgotPasswordHelp } from "@/lib/help-content";
import { TextField } from "@/components/ui/text-field";
import { requestPasswordReset } from "@/lib/api";

const forgotSchema = z.object({
  email: z.string().email("Enter a valid email address.")
});

type ForgotForm = z.infer<typeof forgotSchema>;

export default function ForgotPasswordPage() {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const form = useForm<ForgotForm>({
    resolver: zodResolver(forgotSchema),
    defaultValues: { email: "" }
  });

  async function onSubmit(values: ForgotForm) {
    setSubmitError(null);
    setSubmitSuccess(null);
    try {
      const response = await requestPasswordReset(values);
      setSubmitSuccess(response.message);
      form.reset();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Unable to request password reset.");
    }
  }

  return (
    <section className="rounded-[32px] border border-black/10 bg-white/80 p-8 shadow-panel">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-ink-600">Recovery</p>
          <h1 className="mt-3 font-display text-4xl text-ink-900">Reset your password.</h1>
          <p className="mt-4 text-sm leading-7 text-ink-700">
            Submit your email and the backend will issue a reset token if the account exists.
          </p>
        </div>
        <HelpModal helpContent={forgotPasswordHelp} triggerLabel="Help" />
      </div>
      <form className="mt-8 space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
        {submitError ? <AlertBanner title="Request failed" detail={submitError} tone="error" /> : null}
        {submitSuccess ? <AlertBanner title="Reset email requested" detail={submitSuccess} tone="success" /> : null}
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          error={form.formState.errors.email?.message}
          tooltip="Enter the email address associated with your account. We'll send you instructions to reset your password."
          showTooltip
          {...form.register("email")}
        />
        <Button className="w-full" disabled={form.formState.isSubmitting} type="submit">
          {form.formState.isSubmitting ? "Sending request..." : "Send reset link"}
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
