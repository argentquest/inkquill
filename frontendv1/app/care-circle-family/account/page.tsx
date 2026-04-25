"use client";

import Link from "next/link";
import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { useSession, useToasts } from "@/components/providers/app-providers";
import { PageHeader } from "@/components/shell/page-header";
import { AlertBanner } from "@/components/ui/alert-banner";
import { AccountSummaryPanel } from "@/components/ui/account-summary-panel";
import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { fetchOwnerFamilySummary, sendFamilyInviteEmail } from "@/lib/api";

export default function CareCircleAccountPage() {
  const { user } = useSession();
  const isOwner = user?.is_family_owner === true;
  const { pushToast } = useToasts();
  const [inviteEmail, setInviteEmail] = useState("");

  const ownerSummaryQuery = useQuery({
    queryKey: ["owner-family-summary"],
    queryFn: fetchOwnerFamilySummary,
    enabled: isOwner,
  });

  const inviteMutation = useMutation({
    mutationFn: sendFamilyInviteEmail,
    onSuccess: (data) => {
      setInviteEmail("");
      pushToast({
        title: "Invite sent",
        tone: "success",
        detail: `An invite email was sent to ${data.email}.`,
      });
    },
  });

  const inviteError = inviteMutation.error instanceof Error ? inviteMutation.error.message : null;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Account"
        title="Your Care Circle account"
        description="Manage your profile, billing, and referrals from here."
        action={
          <Link
            className="inline-flex min-w-[160px] items-center justify-center rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
            href="/care-circle-family/account/edit"
          >
            Edit profile
          </Link>
        }
      />
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <AccountSummaryPanel user={user} />
        <div className="space-y-6">
          <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
            <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Family scope</p>
            <h2 className="mt-3 font-display text-3xl text-ink-900">
              {isOwner ? "You own this Care Circle." : "You are a member of this Care Circle."}
            </h2>
            <p className="mt-4 text-sm leading-7 text-ink-700">
              {isOwner
                ? "As the family owner you manage billing, credits, referrals, and who can request access to the whole circle."
                : "Family members can view and manage friend profiles but billing and referrals are handled by the family owner."}
            </p>
            {isOwner && (
              <div className="mt-6 flex flex-wrap gap-3">
                <Link
                  className="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-paper transition hover:bg-ink-700"
                  href="/care-circle-family/billing"
                >
                  Review billing
                </Link>
                <Link
                  className="rounded-full border border-black/10 bg-white/70 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white"
                  href="/care-circle-family/referrals"
                >
                  Open referrals
                </Link>
              </div>
            )}
          </section>

          {isOwner ? (
            <section className="rounded-[28px] border border-black/10 bg-white/80 p-6 shadow-panel">
              <p className="text-xs uppercase tracking-[0.28em] text-ink-600">Family invites</p>
              <h2 className="mt-3 font-display text-3xl text-ink-900">Share your join code or email an invite.</h2>
              <p className="mt-4 text-sm leading-7 text-ink-700">
                Family members can use the join code to request access, or you can send them a direct invitation email.
              </p>

              {ownerSummaryQuery.isLoading ? (
                <p className="mt-6 text-sm text-ink-500">Loading family details...</p>
              ) : ownerSummaryQuery.data ? (
                <div className="mt-6 rounded-[24px] border border-black/10 bg-paper/80 p-5">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-ink-600">Join code</p>
                      <p className="mt-2 font-mono text-3xl font-semibold tracking-[0.32em] text-ink-900">
                        {ownerSummaryQuery.data.join_code}
                      </p>
                      <p className="mt-3 text-sm text-ink-600">{ownerSummaryQuery.data.name}</p>
                    </div>
                    <div className="grid min-w-[180px] gap-3 sm:grid-cols-2">
                      <div className="rounded-2xl border border-black/10 bg-white/80 px-4 py-3">
                        <p className="text-xs uppercase tracking-[0.24em] text-ink-600">Active members</p>
                        <p className="mt-2 text-2xl font-semibold text-ink-900">{ownerSummaryQuery.data.active_member_count}</p>
                      </div>
                      <div className="rounded-2xl border border-black/10 bg-white/80 px-4 py-3">
                        <p className="text-xs uppercase tracking-[0.24em] text-ink-600">Pending requests</p>
                        <p className="mt-2 text-2xl font-semibold text-ink-900">{ownerSummaryQuery.data.pending_request_count}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <AlertBanner title="Family details unavailable" detail="Owner family details could not be loaded." tone="warning" />
              )}

              <form
                className="mt-6 space-y-4"
                onSubmit={(event) => {
                  event.preventDefault();
                  inviteMutation.mutate(inviteEmail.trim());
                }}
              >
                {inviteError ? <AlertBanner title="Invite failed" detail={inviteError} tone="error" /> : null}
                <TextField
                  autoComplete="email"
                  label="Invite by email"
                  name="inviteEmail"
                  onChange={(event) => setInviteEmail(event.target.value)}
                  placeholder="family.member@example.com"
                  type="email"
                  value={inviteEmail}
                />
                <div className="flex flex-wrap gap-3">
                  <Button
                    disabled={!inviteEmail.trim() || inviteMutation.isPending || ownerSummaryQuery.isLoading || !ownerSummaryQuery.data}
                    type="submit"
                  >
                    {inviteMutation.isPending ? "Sending invite..." : "Send invite email"}
                  </Button>
                  <Link
                    className="inline-flex items-center justify-center rounded-full border border-black/10 bg-white/80 px-5 py-3 text-sm font-semibold text-ink-900 transition hover:bg-white"
                    href="/care-circle-family/members"
                  >
                    Review member requests
                  </Link>
                </div>
              </form>
            </section>
          ) : null}
        </div>
      </div>
    </div>
  );
}
