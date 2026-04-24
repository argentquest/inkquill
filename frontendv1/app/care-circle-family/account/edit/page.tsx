"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { AlertBanner } from "@/components/ui/alert-banner";
import { Button } from "@/components/ui/button";
import { SettingsFormSection } from "@/components/ui/settings-form-section";
import { TextField } from "@/components/ui/text-field";
import { updateCurrentUserProfile } from "@/lib/api";

export default function CareCircleEditProfilePage() {
  const router = useRouter();
  const { pushToast } = useToasts();
  const { user, setAuthenticated } = useSession();
  const [displayName, setDisplayName] = useState(user?.display_name ?? user?.username ?? "");
  const [username, setUsername] = useState(user?.username ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const updatedUser = await updateCurrentUserProfile({ display_name: displayName, email, username });
      setAuthenticated(updatedUser);
      pushToast({ title: "Profile updated", tone: "success", detail: "Your Care Circle account details were saved." });
      router.push("/care-circle-family/account");
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to save profile.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Profile settings"
        title="Edit your account profile"
        description="Changes apply across your Care Circle account."
      />
      <SettingsFormSection title="Profile details" description="Update the display name and contact details shown across your Care Circle.">
        <form className="space-y-5" onSubmit={handleSubmit}>
          {error ? <AlertBanner title="Profile update failed" detail={error} tone="error" /> : null}
          <TextField label="Display name" name="displayName" onChange={(e) => setDisplayName(e.target.value)} value={displayName} />
          <TextField label="Username" name="username" onChange={(e) => setUsername(e.target.value)} value={username} />
          <TextField label="Email" name="email" onChange={(e) => setEmail(e.target.value)} value={email} />
          <div className="flex flex-wrap gap-3">
            <Button disabled={submitting} type="submit">
              {submitting ? "Saving..." : "Save profile"}
            </Button>
            <Button onClick={() => router.push("/care-circle-family/account")} type="button" variant="secondary">
              Cancel
            </Button>
          </div>
        </form>
      </SettingsFormSection>
    </div>
  );
}
