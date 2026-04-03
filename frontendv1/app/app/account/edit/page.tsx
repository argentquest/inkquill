"use client";

import { useEffect, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { Button } from "@/components/ui/button";
import { ConfirmationModal } from "@/components/ui/confirmation-modal";
import { ErrorState } from "@/components/ui/error-state";
import { LoadingState } from "@/components/ui/loading-state";
import { SettingsFormSection } from "@/components/ui/settings-form-section";
import { TextField } from "@/components/ui/text-field";
import { updateCurrentUserProfile } from "@/lib/api";

const profileSchema = z.object({
  username: z.string().min(3, "Username must be at least 3 characters."),
  email: z.string().email("Enter a valid email address."),
  display_name: z.string().max(100, "Display name must stay under 100 characters.").optional()
});

type ProfileFormValues = z.infer<typeof profileSchema>;

export default function AccountEditPage() {
  const { error, refreshSession, setAuthenticated, status, user } = useSession();
  const { pushToast } = useToasts();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [confirmResetOpen, setConfirmResetOpen] = useState(false);

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      username: "",
      email: "",
      display_name: ""
    }
  });

  useEffect(() => {
    if (user) {
      form.reset({
        username: user.username,
        email: user.email,
        display_name: user.display_name ?? ""
      });
    }
  }, [form, user]);

  if (status === "loading") {
    return <LoadingState label="Loading profile settings" />;
  }

  if (error || !user) {
    return (
      <ErrorState
        detail={error ?? "No authenticated user is available."}
        onRetry={() => void refreshSession()}
        retryLabel="Reload profile"
        title="Profile settings could not be opened."
      />
    );
  }

  async function handleSubmit(values: ProfileFormValues) {
    setIsSubmitting(true);
    try {
      const updated = await updateCurrentUserProfile({
        username: values.username.trim(),
        email: values.email.trim(),
        display_name: values.display_name?.trim() || undefined
      });
      setAuthenticated(updated);
      pushToast({
        title: "Profile updated",
        tone: "success",
        detail: "Your account settings are now in sync with the shared shell."
      });
      form.reset({
        username: updated.username,
        email: updated.email,
        display_name: updated.display_name ?? ""
      });
    } catch (submitError) {
      pushToast({
        title: "Profile update failed",
        tone: "error",
        detail: submitError instanceof Error ? submitError.message : "Unable to update the profile right now."
      });
    } finally {
      setIsSubmitting(false);
      setConfirmResetOpen(false);
    }
  }

  return (
    <div className="space-y-8">
      <PageHeader
        description="Sprint 3 turns account editing into a real framework route backed by the authenticated profile API, shared validation, and the same shell session state used everywhere else."
        eyebrow="Profile Settings"
        title="Edit the account details the rest of the app depends on."
      />

      <SettingsFormSection
        description="This route establishes the reusable settings form pattern for later commercial, preferences, and admin surfaces."
        title="Profile basics"
      >
        <form
          className="grid gap-5 md:grid-cols-2"
          onSubmit={form.handleSubmit((values) => void handleSubmit(values))}
        >
          <div className="md:col-span-1">
            <TextField
              {...form.register("username")}
              autoComplete="username"
              error={form.formState.errors.username?.message}
              label="Username"
              placeholder="Username"
            />
          </div>
          <div className="md:col-span-1">
            <TextField
              {...form.register("email")}
              autoComplete="email"
              error={form.formState.errors.email?.message}
              label="Email"
              placeholder="Email"
            />
          </div>
          <div className="md:col-span-2">
            <TextField
              {...form.register("display_name")}
              autoComplete="nickname"
              error={form.formState.errors.display_name?.message}
              label="Display name"
              placeholder="How the shell should greet you"
            />
          </div>
          <div className="md:col-span-2 flex flex-wrap justify-between gap-3">
            <Button onClick={() => setConfirmResetOpen(true)} type="button" variant="ghost">
              Reset draft
            </Button>
            <Button disabled={isSubmitting} type="submit">
              {isSubmitting ? "Saving profile..." : "Save profile"}
            </Button>
          </div>
        </form>
      </SettingsFormSection>

      <ConfirmationModal
        body="Discard the current draft and restore the last confirmed account values from the live session."
        confirmLabel="Reset draft"
        onCancel={() => setConfirmResetOpen(false)}
        onConfirm={() => {
          form.reset({
            username: user.username,
            email: user.email,
            display_name: user.display_name ?? ""
          });
          setConfirmResetOpen(false);
        }}
        open={confirmResetOpen}
        title="Reset unsaved profile changes?"
      />
    </div>
  );
}
